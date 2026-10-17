from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from ..database import get_db
from ..models_faze import Faza as FazaModel
from ..schemas_faze import Faza, FazaUpdate, DokumentStavka
from ..security import get_current_user

router = APIRouter(prefix="/api/faze", tags=["faze"], dependencies=[Depends(get_current_user)])


def _faza_u_dict(faza: FazaModel) -> dict:
    """Konvertuje SQLAlchemy model u dict sa parsiranim JSON-om."""
    return {
        "id": faza.id,
        "redni_broj": faza.redni_broj,
        "naziv": faza.naziv,
        "opis": faza.opis,
        "status": faza.status,
        "planirani_pocetak": faza.planirani_pocetak,
        "planirani_kraj": faza.planirani_kraj,
        "stvarni_pocetak": faza.stvarni_pocetak,
        "stvarni_kraj": faza.stvarni_kraj,
        "dokumenti": json.loads(faza.dokumenti or "[]"),
        "napomena": faza.napomena,
        "kreirano": faza.kreirano,
        "izmenjeno": faza.izmenjeno,
    }


@router.get("/", response_model=List[Faza])
def lista_faza(db: Session = Depends(get_db)):
    """Vraća svih 8 faza, sortirano po rednom broju."""
    faze = db.query(FazaModel).order_by(FazaModel.redni_broj).all()
    return [_faza_u_dict(f) for f in faze]


@router.get("/{faza_id}", response_model=Faza)
def detalji_faze(faza_id: int, db: Session = Depends(get_db)):
    faza = db.query(FazaModel).filter(FazaModel.id == faza_id).first()
    if not faza:
        raise HTTPException(status_code=404, detail="Faza nije pronađena")
    return _faza_u_dict(faza)


@router.patch("/{faza_id}", response_model=Faza)
def izmeni_fazu(faza_id: int, izmene: FazaUpdate, db: Session = Depends(get_db)):
    faza = db.query(FazaModel).filter(FazaModel.id == faza_id).first()
    if not faza:
        raise HTTPException(status_code=404, detail="Faza nije pronađena")

    podaci = izmene.model_dump(exclude_unset=True)

    # Ako se menja čeklista, serijalizuj u JSON
    if "dokumenti" in podaci:
        podaci["dokumenti"] = json.dumps([d.model_dump() for d in podaci["dokumenti"]])

    for polje, vrednost in podaci.items():
        setattr(faza, polje, vrednost)

    db.commit()
    db.refresh(faza)
    return _faza_u_dict(faza)