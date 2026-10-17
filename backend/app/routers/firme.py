from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Firma as FirmaModel
from ..models_korisnici import Korisnik
from ..schemas import Firma, FirmaCreate, FirmaUpdate
from ..security import get_current_user

router = APIRouter(prefix="/api/firme", tags=["firme"])

def _firma_u_dict(f: FirmaModel, uneo_ime: str = None) -> dict:
    return {
        "id": f.id, "naziv": f.naziv, "pib": f.pib, "adresa_sedista": f.adresa_sedista,
        "adresa_proizvodnje": f.adresa_proizvodnje, "kontakt_osoba": f.kontakt_osoba,
        "telefon": f.telefon, "email": f.email, "kategorija": f.kategorija,
        "latitude": f.latitude, "longitude": f.longitude, "grad": f.grad,
        "postanski_broj": f.postanski_broj, "broj_licence": f.broj_licence,
        "licenca_vazi_do": f.licenca_vazi_do, "verifikovano": f.verifikovano,
        "napomena": f.napomena, "ocena": f.ocena, "beleške_saradnje": f.beleške_saradnje,
        "kreirano": f.kreirano, "izmenjeno": f.izmenjeno, "uneo_ime": uneo_ime
    }

@router.get("/", response_model=List[Firma])
def lista_firmi(
    kategorija: Optional[str] = None, verifikovano: Optional[str] = None, pretraga: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FirmaModel)
    if kategorija: query = query.filter(FirmaModel.kategorija == kategorija)
    if verifikovano: query = query.filter(FirmaModel.verifikovano == verifikovano)
    if pretraga: query = query.filter(FirmaModel.naziv.ilike(f"%{pretraga}%"))
    
    firme = query.order_by(FirmaModel.naziv).all()
    korisnici = {k.id: k.ime for k in db.query(Korisnik).all()}
    return [_firma_u_dict(f, korisnici.get(f.uneo_id)) for f in firme]

@router.get("/{firma_id}", response_model=Firma)
def detalji_firme(firma_id: int, db: Session = Depends(get_db)):
    firma = db.query(FirmaModel).filter(FirmaModel.id == firma_id).first()
    if not firma: raise HTTPException(status_code=404, detail="Firma nije pronađena")
    korisnik = db.query(Korisnik).filter(Korisnik.id == firma.uneo_id).first()
    return _firma_u_dict(firma, korisnik.ime if korisnik else None)

@router.post("/", response_model=Firma, status_code=201)
def dodaj_firmu(firma: FirmaCreate, db: Session = Depends(get_db), current_user: Korisnik = Depends(get_current_user)):
    nova = FirmaModel(**firma.model_dump())
    nova.uneo_id = current_user.id
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return _firma_u_dict(nova, current_user.ime)

@router.patch("/{firma_id}", response_model=Firma)
def izmeni_firmu(firma_id: int, izmene: FirmaUpdate, db: Session = Depends(get_db)):
    firma = db.query(FirmaModel).filter(FirmaModel.id == firma_id).first()
    if not firma: raise HTTPException(status_code=404, detail="Firma nije pronađena")

    for polje, vrednost in izmene.model_dump(exclude_unset=True).items():
        setattr(firma, polje, vrednost)
    db.commit()
    db.refresh(firma)
    
    korisnik = db.query(Korisnik).filter(Korisnik.id == firma.uneo_id).first()
    return _firma_u_dict(firma, korisnik.ime if korisnik else None)

@router.post("/{firma_id}/verifikuj", response_model=Firma)
def verifikuj_firmu(firma_id: int, db: Session = Depends(get_db)):
    firma = db.query(FirmaModel).filter(FirmaModel.id == firma_id).first()
    if not firma: raise HTTPException(status_code=404, detail="Firma nije pronađena")
    firma.verifikovano = "verifikovano" if firma.verifikovano != "verifikovano" else "neverifikovano"
    db.commit()
    db.refresh(firma)
    return _firma_u_dict(firma, None)

@router.delete("/{firma_id}", status_code=204)
def obrisi_firmu(firma_id: int, db: Session = Depends(get_db)):
    firma = db.query(FirmaModel).filter(FirmaModel.id == firma_id).first()
    if not firma: raise HTTPException(status_code=404, detail="Firma nije pronađena")
    db.delete(firma)
    db.commit()

# Geokodiranje je uklonjeno jer smo odustali od mape