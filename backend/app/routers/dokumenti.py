import os
import uuid
import magic
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..models_dokumenti import Dokument as DokumentModel
from ..models_faze import Faza as FazaModel
from ..models import Firma as FirmaModel
from ..models_troskovi import Trosak as TrosakModel
from ..models_korisnici import Korisnik
from ..schemas_dokumenti import (
    Dokument, DokumentUpdate, DokumentSaPodacima, DokumentPretraga,
)
from ..ocr import izvrsi_ocr
from ..security import get_current_user

router = APIRouter(prefix="/api/dokumenti", tags=["dokumenti"])

DOKUMENTI_DIR = Path("/data/dokumenti")
DOKUMENTI_DIR.mkdir(parents=True, exist_ok=True)

DOZVOLJENI_TIPOVI = {
    "application/pdf", "image/jpeg", "image/png", "image/webp", "image/heic", "image/tiff",
    "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

MAX_VELICINA = 50 * 1024 * 1024


def _dokument_u_dict(dok: DokumentModel, faza=None, firma=None, trosak=None, uneo_ime=None) -> dict:
    return {
        "id": dok.id, "naziv": dok.naziv, "opis": dok.opis, "kategorija": dok.kategorija,
        "originalni_naziv": dok.originalni_naziv, "mime_tip": dok.mime_tip,
        "velicina_bajtova": dok.velicina_bajtova, "ocr_status": dok.ocr_status,
        "faza_id": dok.faza_id, "firma_id": dok.firma_id, "trosak_id": dok.trosak_id,
        "datum_dokumenta": dok.datum_dokumenta, "kreirano": dok.kreirano, "izmenjeno": dok.izmenjeno,
        "faza_naziv": faza.naziv if faza else None, "firma_naziv": firma.naziv if firma else None,
        "trosak_opis": trosak.opis if trosak else None, "uneo_ime": uneo_ime,
    }


def _obradi_ocr(dokument_id: int, putanja: str, mime_tip: str):
    from ..database import SessionLocal
    db = SessionLocal()
    try:
        dok = db.query(DokumentModel).filter(DokumentModel.id == dokument_id).first()
        if not dok: return
        dok.ocr_status = "u_toku"
        db.commit()
        tekst = izvrsi_ocr(putanja, mime_tip)
        dok.ocr_tekst = tekst
        dok.ocr_status = "zavrseno" if tekst else "greska"
        db.commit()
        print(f"[OCR] Dokument {dokument_id} obrađen ({len(tekst)} karaktera)")
    except Exception as e:
        print(f"[OCR] Greška: {e}")
        dok = db.query(DokumentModel).filter(DokumentModel.id == dokument_id).first()
        if dok:
            dok.ocr_status = "greska"
            db.commit()
    finally:
        db.close()


@router.get("/", response_model=List[DokumentSaPodacima])
def lista_dokumenata(
    kategorija: Optional[str] = None, faza_id: Optional[int] = None,
    firma_id: Optional[int] = None, trosak_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(DokumentModel, FazaModel, FirmaModel, TrosakModel, Korisnik)
        .outerjoin(FazaModel, DokumentModel.faza_id == FazaModel.id)
        .outerjoin(FirmaModel, DokumentModel.firma_id == FirmaModel.id)
        .outerjoin(TrosakModel, DokumentModel.trosak_id == TrosakModel.id)
        .outerjoin(Korisnik, DokumentModel.uneo_id == Korisnik.id)
    )
    if kategorija: query = query.filter(DokumentModel.kategorija == kategorija)
    if faza_id: query = query.filter(DokumentModel.faza_id == faza_id)
    if firma_id: query = query.filter(DokumentModel.firma_id == firma_id)
    if trosak_id: query = query.filter(DokumentModel.trosak_id == trosak_id)

    rezultati = query.order_by(DokumentModel.kreirano.desc()).all()
    return [_dokument_u_dict(d, f, fi, t, k.ime if k else None) for d, f, fi, t, k in rezultati]


@router.get("/pretraga/", response_model=List[DokumentPretraga])
def pretraga_dokumenata(q: str, db: Session = Depends(get_db)):
    if not q or len(q) < 2: return []
    pattern = f"%{q}%"
    rezultati = (
        db.query(DokumentModel, FazaModel, FirmaModel, TrosakModel, Korisnik)
        .outerjoin(FazaModel, DokumentModel.faza_id == FazaModel.id)
        .outerjoin(FirmaModel, DokumentModel.firma_id == FirmaModel.id)
        .outerjoin(TrosakModel, DokumentModel.trosak_id == TrosakModel.id)
        .outerjoin(Korisnik, DokumentModel.uneo_id == Korisnik.id)
        .filter(or_(DokumentModel.naziv.ilike(pattern), DokumentModel.opis.ilike(pattern), DokumentModel.ocr_tekst.ilike(pattern)))
        .order_by(DokumentModel.kreirano.desc()).limit(100).all()
    )
    rezultat = []
    for d, f, fi, t, k in rezultati:
        snippet = None
        if d.ocr_tekst and q.lower() in d.ocr_tekst.lower():
            idx = d.ocr_tekst.lower().find(q.lower())
            start, end = max(0, idx - 80), min(len(d.ocr_tekst), idx + len(q) + 80)
            snippet = "..." + d.ocr_tekst[start:end] + "..."
        rezultat.append({"dokument": _dokument_u_dict(d, f, fi, t, k.ime if k else None), "snippet": snippet})
    return rezultat


@router.post("/", response_model=DokumentSaPodacima, status_code=201)
async def upload_dokumenta(
    background_tasks: BackgroundTasks, fajl: UploadFile = File(...), naziv: str = Form(...),
    opis: Optional[str] = Form(None), kategorija: str = Form("ostalo"),
    faza_id: Optional[int] = Form(None), firma_id: Optional[int] = Form(None),
    trosak_id: Optional[int] = Form(None), datum_dokumenta: Optional[str] = Form(None),
    db: Session = Depends(get_db), current_user: Korisnik = Depends(get_current_user),
):
    sadrzaj = await fajl.read()
    if len(sadrzaj) > MAX_VELICINA: raise HTTPException(400, "Fajl je veći od 50 MB")
    mime = magic.from_buffer(sadrzaj[:2048], mime=True)
    if mime not in DOZVOLJENI_TIPOVI: raise HTTPException(400, f"Nedozvoljen tip fajla: {mime}")

    ekstenzija = Path(fajl.filename).suffix.lower()
    jedinstveno_ime = f"{uuid.uuid4().hex}{ekstenzija}"
    putanja = DOKUMENTI_DIR / jedinstveno_ime
    with open(putanja, "wb") as f: f.write(sadrzaj)

    datum_parsed = None
    if datum_dokumenta:
        try: datum_parsed = datetime.fromisoformat(datum_dokumenta)
        except ValueError: pass

    dokument = DokumentModel(
        naziv=naziv, opis=opis, kategorija=kategorija, putanja=str(putanja),
        originalni_naziv=fajl.filename, mime_tip=mime, velicina_bajtova=len(sadrzaj),
        ocr_status="ceka", faza_id=faza_id, firma_id=firma_id, trosak_id=trosak_id,
        datum_dokumenta=datum_parsed, uneo_id=current_user.id,
    )
    db.add(dokument)
    db.commit()
    db.refresh(dokument)

    background_tasks.add_task(_obradi_ocr, dokument.id, str(putanja), mime)

    faza = db.query(FazaModel).filter(FazaModel.id == faza_id).first() if faza_id else None
    firma = db.query(FirmaModel).filter(FirmaModel.id == firma_id).first() if firma_id else None
    trosak = db.query(TrosakModel).filter(TrosakModel.id == trosak_id).first() if trosak_id else None
    return _dokument_u_dict(dokument, faza, firma, trosak, current_user.ime)


@router.get("/{dokument_id}/fajl")
def preuzmi_fajl(dokument_id: int, db: Session = Depends(get_db)):
    dok = db.query(DokumentModel).filter(DokumentModel.id == dokument_id).first()
    if not dok: raise HTTPException(404, "Dokument nije pronađen")
    putanja = Path(dok.putanja)
    if not putanja.exists(): raise HTTPException(404, "Fajl ne postoji na disku")
    return FileResponse(path=putanja, media_type=dok.mime_tip, filename=dok.originalni_naziv)

# Ova ruta je fallback koji si ti dodao i koji rešava problem
@router.get("/{dokument_id}")
def preuzmi_fajl_direktno(dokument_id: int, db: Session = Depends(get_db)):
    """Alternativna ruta ako se poziva samo /api/dokumenti/{id}"""
    return preuzmi_fajl(dokument_id, db)


@router.get("/{dokument_id}/tekst")
def preuzmi_ocr_tekst(dokument_id: int, db: Session = Depends(get_db)):
    dok = db.query(DokumentModel).filter(DokumentModel.id == dokument_id).first()
    if not dok: raise HTTPException(404, "Dokument nije pronađen")
    return {"status": dok.ocr_status, "tekst": dok.ocr_tekst or "", "duzina": len(dok.ocr_tekst or "")}


@router.patch("/{dokument_id}", response_model=DokumentSaPodacima)
def izmeni_dokument(dokument_id: int, izmene: DokumentUpdate, db: Session = Depends(get_db)):
    dok = db.query(DokumentModel).filter(DokumentModel.id == dokument_id).first()
    if not dok: raise HTTPException(404, "Dokument nije pronađen")
    for polje, vrednost in izmene.model_dump(exclude_unset=True).items():
        setattr(dok, polje, vrednost)
    db.commit()
    db.refresh(dok)
    faza = db.query(FazaModel).filter(FazaModel.id == dok.faza_id).first() if dok.faza_id else None
    firma = db.query(FirmaModel).filter(FirmaModel.id == dok.firma_id).first() if dok.firma_id else None
    trosak = db.query(TrosakModel).filter(TrosakModel.id == dok.trosak_id).first() if dok.trosak_id else None
    korisnik = db.query(Korisnik).filter(Korisnik.id == dok.uneo_id).first()
    return _dokument_u_dict(dok, faza, firma, trosak, korisnik.ime if korisnik else None)


@router.post("/{dokument_id}/pokreni-ocr")
def ponovo_pokreni_ocr(dokument_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    dok = db.query(DokumentModel).filter(DokumentModel.id == dokument_id).first()
    if not dok: raise HTTPException(404, "Dokument nije pronađen")
    dok.ocr_status = "ceka"
    db.commit()
    background_tasks.add_task(_obradi_ocr, dok.id, dok.putanja, dok.mime_tip)
    return {"status": "OCR pokrenut u pozadini"}


@router.delete("/{dokument_id}", status_code=204)
def obrisi_dokument(dokument_id: int, db: Session = Depends(get_db)):
    dok = db.query(DokumentModel).filter(DokumentModel.id == dokument_id).first()
    if not dok: raise HTTPException(404, "Dokument nije pronađen")
    try: Path(dok.putanja).unlink(missing_ok=True)
    except Exception as e: print(f"Greška pri brisanju fajla: {e}")
    db.delete(dok)
    db.commit()