from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from ..database import get_db
from ..models_kapital import Kapital as KapitalModel
from ..models_troskovi import Trosak as TrosakModel, Budzet as BudzetModel
from ..schemas_kapital import (
    Kapital, KapitalCreate, KapitalUpdate, RezimeFinansija,
)
from ..security import get_current_user

router = APIRouter(prefix="/api/kapital", tags=["kapital"], dependencies=[Depends(get_current_user)])


@router.get("/", response_model=List[Kapital])
def lista_kapitala(db: Session = Depends(get_db)):
    return db.query(KapitalModel).order_by(KapitalModel.datum.desc()).all()


@router.post("/", response_model=Kapital, status_code=201)
def dodaj_kapital(kapital: KapitalCreate, db: Session = Depends(get_db)):
    novi = KapitalModel(**kapital.model_dump())
    db.add(novi)
    db.commit()
    db.refresh(novi)
    return novi


@router.patch("/{kapital_id}", response_model=Kapital)
def izmeni_kapital(kapital_id: int, izmene: KapitalUpdate, db: Session = Depends(get_db)):
    kapital = db.query(KapitalModel).filter(KapitalModel.id == kapital_id).first()
    if not kapital:
        raise HTTPException(status_code=404, detail="Kapital nije pronađen")

    for polje, vrednost in izmene.model_dump(exclude_unset=True).items():
        setattr(kapital, polje, vrednost)

    db.commit()
    db.refresh(kapital)
    return kapital


@router.delete("/{kapital_id}", status_code=204)
def obrisi_kapital(kapital_id: int, db: Session = Depends(get_db)):
    kapital = db.query(KapitalModel).filter(KapitalModel.id == kapital_id).first()
    if not kapital:
        raise HTTPException(status_code=404, detail="Kapital nije pronađen")
    db.delete(kapital)
    db.commit()


@router.get("/rezime/", response_model=RezimeFinansija)
def rezime_finansija(db: Session = Depends(get_db)):
    """Rezime: koliko imaš, koliko si potrošio, koliko ti treba."""
    ukupan_kapital = db.query(func.coalesce(func.sum(KapitalModel.iznos), 0)).scalar()

    ukupni_troskovi = (
        db.query(func.coalesce(func.sum(TrosakModel.iznos), 0))
        .filter(TrosakModel.status != "planirano")
        .scalar()
    )

    ukupan_budzet = db.query(func.coalesce(func.sum(BudzetModel.planirani_iznos), 0)).scalar()

    preostalo = ukupan_kapital - ukupni_troskovi
    procenat = (ukupni_troskovi / ukupan_kapital * 100) if ukupan_kapital > 0 else 0
    kapital_vs_budzet = ukupan_kapital - ukupan_budzet

    return RezimeFinansija(
        ukupan_kapital=ukupan_kapital,
        ukupni_troskovi=ukupni_troskovi,
        preostalo=preostalo,
        procenat_potroseno=round(procenat, 1),
        ukupan_budzet=ukupan_budzet,
        kapital_vs_budzet=kapital_vs_budzet,
    )