from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FirmaBase(BaseModel):
    naziv: str
    pib: Optional[str] = None
    adresa_sedista: Optional[str] = None
    adresa_proizvodnje: Optional[str] = None
    kontakt_osoba: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    kategorija: str = "izvođač"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    grad: Optional[str] = None
    postanski_broj: Optional[str] = None
    broj_licence: Optional[str] = None
    licenca_vazi_do: Optional[datetime] = None
    verifikovano: str = "neverifikovano"
    napomena: Optional[str] = None
    ocena: Optional[int] = None
    beleške_saradnje: Optional[str] = None


class FirmaCreate(FirmaBase):
    pass


class FirmaUpdate(BaseModel):
    naziv: Optional[str] = None
    pib: Optional[str] = None
    adresa_sedista: Optional[str] = None
    adresa_proizvodnje: Optional[str] = None
    kontakt_osoba: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    kategorija: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    grad: Optional[str] = None
    postanski_broj: Optional[str] = None
    broj_licence: Optional[str] = None
    licenca_vazi_do: Optional[datetime] = None
    verifikovano: Optional[str] = None
    napomena: Optional[str] = None
    ocena: Optional[int] = None
    beleške_saradnje: Optional[str] = None


class Firma(FirmaBase):
    id: int
    kreirano: datetime
    izmenjeno: datetime
    uneo_ime: Optional[str] = None  # <--- DODATO

    class Config:
        from_attributes = True