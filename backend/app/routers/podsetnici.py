from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Optional

from ..database import get_db
from ..models_podsetnici import Podsetnik as PodsetnikModel
from ..models_faze import Faza as FazaModel
from ..models import Firma as FirmaModel
from ..schemas_podsetnici import (
    Podsetnik, PodsetnikCreate, PodsetnikUpdate,
    PodsetnikSaPodacima, RezimePodsetnika,
)
from ..security import get_current_user

router = APIRouter(prefix="/api/podsetnici", tags=["podsetnici"], dependencies=[Depends(get_current_user)])


def _podsetnik_u_dict(podsetnik: PodsetnikModel, faza=None, firma=None) -> dict:
    danas = date.today()
    dani = (podsetnik.datum_dospeca - danas).days

    return {
        "id": podsetnik.id,
        "naslov": podsetnik.naslov,
        "opis": podsetnik.opis,
        "faza_id": podsetnik.faza_id,
        "firma_id": podsetnik.firma_id,
        "datum_dospeca": podsetnik.datum_dospeca,
        "vreme_dospeca": podsetnik.vreme_dospeca,
        "prioritet": podsetnik.prioritet,
        "kategorija": podsetnik.kategorija,
        "zavrseno": podsetnik.zavrseno,
        "datum_zavrsetka": podsetnik.datum_zavrsetka,
        "automatski": podsetnik.automatski,
        "podseti_dana_pre": podsetnik.podseti_dana_pre,
        "kreirano": podsetnik.kreirano,
        "izmenjeno": podsetnik.izmenjeno,
        "faza_naziv": faza.naziv if faza else None,
        "firma_naziv": firma.naziv if firma else None,
        "dani_do_dospeca": dani,
        "kasni": dani < 0 and not podsetnik.zavrseno,
    }


@router.get("/", response_model=List[PodsetnikSaPodacima])
def lista_podsetnika(
    zavrseno: Optional[bool] = None,
    kategorija: Optional[str] = None,
    prioritet: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista podsetnika, sortirano po datumu dospeća."""
    query = (
        db.query(PodsetnikModel, FazaModel, FirmaModel)
        .outerjoin(FazaModel, PodsetnikModel.faza_id == FazaModel.id)
        .outerjoin(FirmaModel, PodsetnikModel.firma_id == FirmaModel.id)
    )

    if zavrseno is not None:
        query = query.filter(PodsetnikModel.zavrseno == zavrseno)
    if kategorija:
        query = query.filter(PodsetnikModel.kategorija == kategorija)
    if prioritet:
        query = query.filter(PodsetnikModel.prioritet == prioritet)

    rezultati = query.order_by(PodsetnikModel.datum_dospeca.asc()).all()
    return [_podsetnik_u_dict(p, f, fi) for p, f, fi in rezultati]


@router.get("/rezime/", response_model=RezimePodsetnika)
def rezime_podsetnika(db: Session = Depends(get_db)):
    """Rezime — koliko danas, sutra, ove nedelje, koliko kasni."""
    danas = date.today()
    sutra = danas + timedelta(days=1)
    za_nedelju = danas + timedelta(days=7)

    aktivni = db.query(PodsetnikModel).filter(PodsetnikModel.zavrseno == False).all()  # noqa

    danas_count = sum(1 for p in aktivni if p.datum_dospeca == danas)
    sutra_count = sum(1 for p in aktivni if p.datum_dospeca == sutra)
    nedelja_count = sum(1 for p in aktivni if danas <= p.datum_dospeca <= za_nedelju)
    kasni_count = sum(1 for p in aktivni if p.datum_dospeca < danas)

    return RezimePodsetnika(
        danas=danas_count,
        sutra=sutra_count,
        ove_nedelje=nedelja_count,
        kasni=kasni_count,
        ukupno_aktivnih=len(aktivni),
    )


@router.post("/", response_model=PodsetnikSaPodacima, status_code=201)
def dodaj_podsetnik(podsetnik: PodsetnikCreate, db: Session = Depends(get_db)):
    novi = PodsetnikModel(**podsetnik.model_dump())
    db.add(novi)
    db.commit()
    db.refresh(novi)

    faza = db.query(FazaModel).filter(FazaModel.id == novi.faza_id).first() if novi.faza_id else None
    firma = db.query(FirmaModel).filter(FirmaModel.id == novi.firma_id).first() if novi.firma_id else None
    return _podsetnik_u_dict(novi, faza, firma)


@router.patch("/{podsetnik_id}", response_model=PodsetnikSaPodacima)
def izmeni_podsetnik(podsetnik_id: int, izmene: PodsetnikUpdate, db: Session = Depends(get_db)):
    podsetnik = db.query(PodsetnikModel).filter(PodsetnikModel.id == podsetnik_id).first()
    if not podsetnik:
        raise HTTPException(status_code=404, detail="Podsetnik nije pronađen")

    podaci = izmene.model_dump(exclude_unset=True)

    # Ako se označava kao završen, postavi datum
    if "zavrseno" in podaci:
        if podaci["zavrseno"] and not podsetnik.zavrseno:
            podsetnik.datum_zavrsetka = datetime.utcnow()
        elif not podaci["zavrseno"]:
            podsetnik.datum_zavrsetka = None

    for polje, vrednost in podaci.items():
        setattr(podsetnik, polje, vrednost)

    db.commit()
    db.refresh(podsetnik)

    faza = db.query(FazaModel).filter(FazaModel.id == podsetnik.faza_id).first() if podsetnik.faza_id else None
    firma = db.query(FirmaModel).filter(FirmaModel.id == podsetnik.firma_id).first() if podsetnik.firma_id else None
    return _podsetnik_u_dict(podsetnik, faza, firma)


@router.post("/{podsetnik_id}/zavrsi", response_model=PodsetnikSaPodacima)
def zavrsi_podsetnik(podsetnik_id: int, db: Session = Depends(get_db)):
    """Brzo označavanje kao završeno."""
    podsetnik = db.query(PodsetnikModel).filter(PodsetnikModel.id == podsetnik_id).first()
    if not podsetnik:
        raise HTTPException(status_code=404, detail="Podsetnik nije pronađen")

    podsetnik.zavrseno = not podsetnik.zavrseno
    podsetnik.datum_zavrsetka = datetime.utcnow() if podsetnik.zavrseno else None
    db.commit()
    db.refresh(podsetnik)

    faza = db.query(FazaModel).filter(FazaModel.id == podsetnik.faza_id).first() if podsetnik.faza_id else None
    firma = db.query(FirmaModel).filter(FirmaModel.id == podsetnik.firma_id).first() if podsetnik.firma_id else None
    return _podsetnik_u_dict(podsetnik, faza, firma)


@router.delete("/{podsetnik_id}", status_code=204)
def obrisi_podsetnik(podsetnik_id: int, db: Session = Depends(get_db)):
    podsetnik = db.query(PodsetnikModel).filter(PodsetnikModel.id == podsetnik_id).first()
    if not podsetnik:
        raise HTTPException(status_code=404, detail="Podsetnik nije pronađen")
    db.delete(podsetnik)
    db.commit()


# ===== AUTOMATSKI PODSETNICI IZ ZAKONA =====

@router.post("/generisi-zakonske/", status_code=201)
def generisi_zakonske_podsetnike(db: Session = Depends(get_db)):
    """
    Generiše zakonske podsetnike na osnovu faza.
    Poziva se ručno ili pri startu.
    """
    generisani = []

    # Faza 7 — Prijava radova (8 dana pre početka radova)
    faza7 = db.query(FazaModel).filter(FazaModel.redni_broj == 7).first()
    if faza7 and faza7.planirani_pocetak:
        datum = faza7.planirani_pocetak - timedelta(days=8)
        # Proveri da već ne postoji
        postoji = (
            db.query(PodsetnikModel)
            .filter(PodsetnikModel.faza_id == faza7.id)
            .filter(PodsetnikModel.naslov.like("%Prijava radova%"))
            .first()
        )
        if not postoji:
            novi = PodsetnikModel(
                naslov="Prijava radova (CIS) — 8 dana pre početka",
                opis=f"Zakonska obaveza: prijava radova najmanje 8 dana pre početka radova na Fazi 7.",
                faza_id=faza7.id,
                datum_dospeca=datum,
                prioritet="hitno",
                kategorija="zakonski",
                automatski=True,
                podseti_dana_pre=7,
            )
            db.add(novi)
            generisani.append("Prijava radova")

    db.commit()
    return {"generisano": generisani, "broj": len(generisani)}