from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class DokumentStavka(BaseModel):
    """Jedna stavka u čeklisti dokumenata."""
    naziv: str
    zavrseno: bool = False


class FazaBase(BaseModel):
    naziv: str
    opis: Optional[str] = None
    status: str = "nije_početo"
    planirani_pocetak: Optional[date] = None
    planirani_kraj: Optional[date] = None
    stvarni_pocetak: Optional[date] = None
    stvarni_kraj: Optional[date] = None
    dokumenti: List[DokumentStavka] = []
    napomena: Optional[str] = None


class FazaUpdate(BaseModel):
    """Sva polja opciona — menjaš samo ono što pošalješ."""
    naziv: Optional[str] = None
    opis: Optional[str] = None
    status: Optional[str] = None
    planirani_pocetak: Optional[date] = None
    planirani_kraj: Optional[date] = None
    stvarni_pocetak: Optional[date] = None
    stvarni_kraj: Optional[date] = None
    dokumenti: Optional[List[DokumentStavka]] = None
    napomena: Optional[str] = None


class Faza(FazaBase):
    id: int
    redni_broj: int
    kreirano: datetime
    izmenjeno: datetime

    class Config:
        from_attributes = True