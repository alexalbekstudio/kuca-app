from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class KapitalBase(BaseModel):
    naziv: str
    iznos: int
    kategorija: str = "usteda"
    datum: date
    napomena: Optional[str] = None


class KapitalCreate(KapitalBase):
    pass


class KapitalUpdate(BaseModel):
    naziv: Optional[str] = None
    iznos: Optional[int] = None
    kategorija: Optional[str] = None
    datum: Optional[date] = None
    napomena: Optional[str] = None


class Kapital(KapitalBase):
    id: int
    kreirano: datetime
    izmenjeno: datetime

    class Config:
        from_attributes = True


class RezimeFinansija(BaseModel):
    """Ukupan rezime — kapital vs. troškovi."""
    ukupan_kapital: int
    ukupni_troskovi: int
    preostalo: int
    procenat_potroseno: float
    ukupan_budzet: int  # planirani budžet iz faza
    kapital_vs_budzet: int  # razlika