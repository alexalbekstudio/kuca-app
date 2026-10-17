from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models_veze import FazaFirma as FazaFirmaModel
from ..models import Firma as FirmaModel
from ..models_faze import Faza as FazaModel
from ..schemas_veze import FazaFirmaCreate, FazaFirmaUpdate, FazaFirmaSaPodacima
from ..security import get_current_user

router = APIRouter(prefix="/api/veze", tags=["veze"], dependencies=[Depends(get_current_user)])


def _veza_u_dict(veza: FazaFirmaModel, firma: FirmaModel) -> dict:
    return {
        "id": veza.id,
        "faza_id": veza.faza_id,
        "firma_id": veza.firma_id,
        "uloga": veza.uloga,
        "napomena": veza.napomena,
        "cena": veza.cena,
        "kreirano": veza.kreirano,
        "firma_naziv": firma.naziv,
        "firma_kategorija": firma.kategorija,
        "firma_telefon": firma.telefon,
        "firma_kontakt": firma.kontakt_osoba,
    }


@router.get("/faza/{faza_id}", response_model=List[FazaFirmaSaPodacima])
def firme_u_fazi(faza_id: int, db: Session = Depends(get_db)):
    """Vraća sve firme angažovane u datoj fazi."""
    veze = (
        db.query(FazaFirmaModel, FirmaModel)
        .join(FirmaModel, FazaFirmaModel.firma_id == FirmaModel.id)
        .filter(FazaFirmaModel.faza_id == faza_id)
        .all()
    )
    return [_veza_u_dict(v, f) for v, f in veze]


@router.post("/faza/{faza_id}", response_model=FazaFirmaSaPodacima, status_code=201)
def dodaj_firmu_u_fazu(faza_id: int, veza: FazaFirmaCreate, db: Session = Depends(get_db)):
    """Angažuje firmu za datu fazu."""
    # Provera da faza postoji
    faza = db.query(FazaModel).filter(FazaModel.id == faza_id).first()
    if not faza:
        raise HTTPException(status_code=404, detail="Faza nije pronađena")

    # Provera da firma postoji
    firma = db.query(FirmaModel).filter(FirmaModel.id == veza.firma_id).first()
    if not firma:
        raise HTTPException(status_code=404, detail="Firma nije pronađena")

    # Provera da veza već ne postoji
    postoji = (
        db.query(FazaFirmaModel)
        .filter(FazaFirmaModel.faza_id == faza_id, FazaFirmaModel.firma_id == veza.firma_id)
        .first()
    )
    if postoji:
        raise HTTPException(status_code=400, detail="Firma je već angažovana u ovoj fazi")

    nova = FazaFirmaModel(
        faza_id=faza_id,
        firma_id=veza.firma_id,
        uloga=veza.uloga,
        napomena=veza.napomena,
        cena=veza.cena,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return _veza_u_dict(nova, firma)


@router.patch("/{veza_id}", response_model=FazaFirmaSaPodacima)
def izmeni_vezu(veza_id: int, izmene: FazaFirmaUpdate, db: Session = Depends(get_db)):
    """Menja ulogu, napomenu ili cenu veze."""
    veza = db.query(FazaFirmaModel).filter(FazaFirmaModel.id == veza_id).first()
    if not veza:
        raise HTTPException(status_code=404, detail="Veza nije pronađena")

    for polje, vrednost in izmene.model_dump(exclude_unset=True).items():
        setattr(veza, polje, vrednost)

    db.commit()
    db.refresh(veza)

    firma = db.query(FirmaModel).filter(FirmaModel.id == veza.firma_id).first()
    return _veza_u_dict(veza, firma)


@router.delete("/{veza_id}", status_code=204)
def obrisi_vezu(veza_id: int, db: Session = Depends(get_db)):
    """Uklanja firmu iz faze."""
    veza = db.query(FazaFirmaModel).filter(FazaFirmaModel.id == veza_id).first()
    if not veza:
        raise HTTPException(status_code=404, detail="Veza nije pronađena")
    db.delete(veza)
    db.commit()