from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models_materijali import Materijal as MaterijalModel, Ponuda as PonudaModel
from ..models import Firma as FirmaModel
from ..models_korisnici import Korisnik
from ..schemas_materijali import (
    Materijal, MaterijalCreate, MaterijalSaPonudama,
    Ponuda, PonudaCreate,
)
from ..security import get_current_user

router = APIRouter(prefix="/api/materijali", tags=["materijali"])


def _ponuda_u_dict(p: PonudaModel, firma=None, korisnik=None) -> dict:
    return {
        "id": p.id, "materijal_id": p.materijal_id, "firma_id": p.firma_id,
        "cena": p.cena, "datum_ponude": p.datum_ponude, "napomena": p.napomena,
        "rok_isporuke": p.rok_isporuke, "kreirano": p.kreirano,
        "firma_naziv": firma.naziv if firma else None,
        "uneo_ime": korisnik.ime if korisnik else None,
    }


@router.get("/", response_model=List[MaterijalSaPonudama])
def lista_materijala(db: Session = Depends(get_db)):
    materijali = db.query(MaterijalModel).order_by(MaterijalModel.naziv).all()
    korisnici = {k.id: k.ime for k in db.query(Korisnik).all()}

    rezultat = []
    for m in materijali:
        ponude_db = db.query(PonudaModel).filter(PonudaModel.materijal_id == m.id).all()
        ponude = []
        najbolja = None
        najbolja_firma = None

        for p in ponude_db:
            firma = db.query(FirmaModel).filter(FirmaModel.id == p.firma_id).first() if p.firma_id else None
            pd = _ponuda_u_dict(p, firma, None)
            pd["uneo_ime"] = korisnici.get(p.uneo_id)
            ponude.append(pd)

            if najbolja is None or p.cena < najbolja:
                najbolja = p.cena
                najbolja_firma = firma.naziv if firma else None

        ponude.sort(key=lambda x: x["cena"])
        rezultat.append({
            "id": m.id, "naziv": m.naziv, "jedinica": m.jedinica,
            "kategorija": m.kategorija, "opis": m.opis,
            "kreirano": m.kreirano, "uneo_ime": korisnici.get(m.uneo_id),
            "ponude": ponude, "najbolja_cena": najbolja, "najbolja_firma": najbolja_firma,
        })
    return rezultat


@router.post("/", response_model=Materijal, status_code=201)
def dodaj_materijal(m: MaterijalCreate, db: Session = Depends(get_db), current_user: Korisnik = Depends(get_current_user)):
    novi = MaterijalModel(**m.model_dump())
    novi.uneo_id = current_user.id
    db.add(novi)
    db.commit()
    db.refresh(novi)
    return {"id": novi.id, "naziv": novi.naziv, "jedinica": novi.jedinica,
            "kategorija": novi.kategorija, "opis": novi.opis,
            "kreirano": novi.kreirano, "uneo_ime": current_user.ime}


@router.post("/{materijal_id}/ponude", response_model=Ponuda, status_code=201)
def dodaj_ponudu(materijal_id: int, p: PonudaCreate, db: Session = Depends(get_db), current_user: Korisnik = Depends(get_current_user)):
    materijal = db.query(MaterijalModel).filter(MaterijalModel.id == materijal_id).first()
    if not materijal:
        raise HTTPException(404, "Materijal nije pronađen")

    nova = PonudaModel(**p.model_dump())
    nova.materijal_id = materijal_id
    nova.uneo_id = current_user.id
    db.add(nova)
    db.commit()
    db.refresh(nova)

    firma = db.query(FirmaModel).filter(FirmaModel.id == nova.firma_id).first() if nova.firma_id else None
    return _ponuda_u_dict(nova, firma, current_user)


@router.delete("/ponude/{ponuda_id}", status_code=204)
def obrisi_ponudu(ponuda_id: int, db: Session = Depends(get_db)):
    p = db.query(PonudaModel).filter(PonudaModel.id == ponuda_id).first()
    if not p:
        raise HTTPException(404, "Ponuda nije pronađena")
    db.delete(p)
    db.commit()


@router.delete("/{materijal_id}", status_code=204)
def obrisi_materijal(materijal_id: int, db: Session = Depends(get_db)):
    m = db.query(MaterijalModel).filter(MaterijalModel.id == materijal_id).first()
    if not m:
        raise HTTPException(404, "Materijal nije pronađen")
    db.delete(m)
    db.commit()