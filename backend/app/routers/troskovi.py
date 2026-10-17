from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..database import get_db
from ..models_troskovi import Trosak as TrosakModel, Budzet as BudzetModel
from ..models_faze import Faza as FazaModel
from ..models import Firma as FirmaModel
from ..models_korisnici import Korisnik
from ..schemas_troskovi import (
    Trosak, TrosakCreate, TrosakUpdate, TrosakSaPodacima,
    Budzet, BudzetCreate, BudzetUpdate,
    RezimeFaze, RezimeUkupno,
)
from ..security import get_current_user

router = APIRouter(prefix="/api/troskovi", tags=["troskovi"])


def _trosak_u_dict(trosak: TrosakModel, faza=None, firma=None, uneo_ime=None) -> dict:
    return {
        "id": trosak.id, "opis": trosak.opis, "kategorija": trosak.kategorija,
        "iznos": trosak.iznos, "datum_troska": trosak.datum_troska,
        "datum_placanja": trosak.datum_placanja, "status": trosak.status,
        "broj_dokumenta": trosak.broj_dokumenta, "napomena": trosak.napomena,
        "faza_id": trosak.faza_id, "firma_id": trosak.firma_id,
        "kreirano": trosak.kreirano, "izmenjeno": trosak.izmenjeno,
        "faza_naziv": faza.naziv if faza else None, "firma_naziv": firma.naziv if firma else None,
        "uneo_ime": uneo_ime
    }


@router.get("/", response_model=List[TrosakSaPodacima])
def lista_troskova(
    faza_id: Optional[int] = None, firma_id: Optional[int] = None,
    kategorija: Optional[str] = None, status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = (
        db.query(TrosakModel, FazaModel, FirmaModel, Korisnik)
        .outerjoin(FazaModel, TrosakModel.faza_id == FazaModel.id)
        .outerjoin(FirmaModel, TrosakModel.firma_id == FirmaModel.id)
        .outerjoin(Korisnik, TrosakModel.uneo_id == Korisnik.id)
    )
    if faza_id: query = query.filter(TrosakModel.faza_id == faza_id)
    if firma_id: query = query.filter(TrosakModel.firma_id == firma_id)
    if kategorija: query = query.filter(TrosakModel.kategorija == kategorija)
    if status: query = query.filter(TrosakModel.status == status)

    rezultati = query.order_by(TrosakModel.datum_troska.desc()).all()
    return [_trosak_u_dict(t, f, fi, k.ime if k else None) for t, f, fi, k in rezultati]


@router.post("/", response_model=TrosakSaPodacima, status_code=201)
def dodaj_trosak(trosak: TrosakCreate, db: Session = Depends(get_db), current_user: Korisnik = Depends(get_current_user)):
    novi = TrosakModel(**trosak.model_dump())
    novi.uneo_id = current_user.id
    db.add(novi)
    db.commit()
    db.refresh(novi)

    faza = db.query(FazaModel).filter(FazaModel.id == novi.faza_id).first() if novi.faza_id else None
    firma = db.query(FirmaModel).filter(FirmaModel.id == novi.firma_id).first() if novi.firma_id else None
    return _trosak_u_dict(novi, faza, firma, current_user.ime)


@router.patch("/{trosak_id}", response_model=TrosakSaPodacima)
def izmeni_trosak(trosak_id: int, izmene: TrosakUpdate, db: Session = Depends(get_db)):
    trosak = db.query(TrosakModel).filter(TrosakModel.id == trosak_id).first()
    if not trosak: raise HTTPException(status_code=404, detail="Trošak nije pronađen")

    for polje, vrednost in izmene.model_dump(exclude_unset=True).items():
        setattr(trosak, polje, vrednost)

    db.commit()
    db.refresh(trosak)
    faza = db.query(FazaModel).filter(FazaModel.id == trosak.faza_id).first() if trosak.faza_id else None
    firma = db.query(FirmaModel).filter(FirmaModel.id == trosak.firma_id).first() if trosak.firma_id else None
    korisnik = db.query(Korisnik).filter(Korisnik.id == trosak.uneo_id).first()
    return _trosak_u_dict(trosak, faza, firma, korisnik.ime if korisnik else None)


@router.delete("/{trosak_id}", status_code=204)
def obrisi_trosak(trosak_id: int, db: Session = Depends(get_db)):
    trosak = db.query(TrosakModel).filter(TrosakModel.id == trosak_id).first()
    if not trosak: raise HTTPException(status_code=404, detail="Trošak nije pronađen")
    db.delete(trosak)
    db.commit()


# ===== BUDŽET =====
@router.get("/budzeti/", response_model=List[Budzet])
def lista_budzeta(db: Session = Depends(get_db)):
    return db.query(BudzetModel).all()

@router.post("/budzeti/", response_model=Budzet, status_code=201)
def postavi_budzet(budzet: BudzetCreate, db: Session = Depends(get_db)):
    faza = db.query(FazaModel).filter(FazaModel.id == budzet.faza_id).first()
    if not faza: raise HTTPException(status_code=404, detail="Faza nije pronađena")
    postojeci = db.query(BudzetModel).filter(BudzetModel.faza_id == budzet.faza_id).first()
    if postojeci:
        for polje, vrednost in budzet.model_dump().items():
            setattr(postojeci, polje, vrednost)
        db.commit()
        db.refresh(postojeci)
        return postojeci
    novi = BudzetModel(**budzet.model_dump())
    db.add(novi)
    db.commit()
    db.refresh(novi)
    return novi


# ===== REZIME =====
@router.get("/rezime/", response_model=RezimeUkupno)
def rezime(db: Session = Depends(get_db)):
    faze = db.query(FazaModel).order_by(FazaModel.redni_broj).all()
    po_fazama, ukupan_budzet, ukupni_troskovi = [], 0, 0

    for faza in faze:
        budzet = db.query(BudzetModel).filter(BudzetModel.faza_id == faza.id).first()
        planirano = budzet.planirani_iznos if budzet else 0
        stvarni = db.query(func.coalesce(func.sum(TrosakModel.iznos), 0)).filter(TrosakModel.faza_id == faza.id, TrosakModel.status != "planirano").scalar()
        broj = db.query(func.count(TrosakModel.id)).filter(TrosakModel.faza_id == faza.id, TrosakModel.status != "planirano").scalar()
        procenat = (stvarni / planirano * 100) if planirano > 0 else 0

        po_fazama.append(RezimeFaze(
            faza_id=faza.id, faza_naziv=faza.naziv, faza_redni_broj=faza.redni_broj,
            planirani_budzet=planirano, stvarni_troskovi=stvarni, broj_troskova=broj, procenat_iskoriscenja=round(procenat, 1)
        ))
        ukupan_budzet += planirano
        ukupni_troskovi += stvarni

    van_faze = db.query(func.coalesce(func.sum(TrosakModel.iznos), 0)).filter(TrosakModel.faza_id.is_(None), TrosakModel.status != "planirano").scalar()
    ukupni_troskovi += van_faze
    preostalo = ukupan_budzet - ukupni_troskovi
    procenat = (ukupni_troskovi / ukupan_budzet * 100) if ukupan_budzet > 0 else 0

    return RezimeUkupno(
        ukupan_budzet=ukupan_budzet, ukupni_troskovi=ukupni_troskovi, preostalo=preostalo,
        procenat_iskoriscenja=round(procenat, 1), po_fazama=po_fazama
    )