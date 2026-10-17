from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional


class PodsetnikBase(BaseModel):
    naslov: str
    opis: Optional[str] = None
    faza_id: Optional[int] = None
    firma_id: Optional[int] = None
    datum_dospeca: date
    vreme_dospeca: Optional[time] = None
    prioritet: str = "srednje"
    kategorija: str = "opste"
    podseti_dana_pre: int = 3


class PodsetnikCreate(PodsetnikBase):
    pass


class PodsetnikUpdate(BaseModel):
    naslov: Optional[str] = None
    opis: Optional[str] = None
    faza_id: Optional[int] = None
    firma_id: Optional[int] = None
    datum_dospeca: Optional[date] = None
    vreme_dospeca: Optional[time] = None
    prioritet: Optional[str] = None
    kategorija: Optional[str] = None
    zavrseno: Optional[bool] = None
    podseti_dana_pre: Optional[int] = None


class Podsetnik(PodsetnikBase):
    id: int
    zavrseno: bool
    datum_zavrsetka: Optional[datetime] = None
    automatski: bool
    kreirano: datetime
    izmenjeno: datetime

    class Config:
        from_attributes = True


class PodsetnikSaPodacima(Podsetnik):
    """Proširena verzija sa nazivima faze i firme, i danima do dospeća."""
    faza_naziv: Optional[str] = None
    firma_naziv: Optional[str] = None
    dani_do_dospeca: int  # negativno ako je prošlo
    kasni: bool


class RezimePodsetnika(BaseModel):
    """Rezime za prikaz na vrhu."""
    danas: int
    sutra: int
    ove_nedelje: int
    kasni: int
    ukupno_aktivnih: int