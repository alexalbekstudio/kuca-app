from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class TrosakBase(BaseModel):
    opis: str
    kategorija: str = "materijal"
    iznos: int
    datum_troska: date
    datum_placanja: Optional[date] = None
    status: str = "planirano"
    broj_dokumenta: Optional[str] = None
    napomena: Optional[str] = None
    faza_id: Optional[int] = None
    firma_id: Optional[int] = None


class TrosakCreate(TrosakBase):
    pass


class TrosakUpdate(BaseModel):
    opis: Optional[str] = None
    kategorija: Optional[str] = None
    iznos: Optional[int] = None
    datum_troska: Optional[date] = None
    datum_placanja: Optional[date] = None
    status: Optional[str] = None
    broj_dokumenta: Optional[str] = None
    napomena: Optional[str] = None
    faza_id: Optional[int] = None
    firma_id: Optional[int] = None


class Trosak(TrosakBase):
    id: int
    kreirano: datetime
    izmenjeno: datetime
    uneo_ime: Optional[str] = None  # <--- DODATO

    class Config:
        from_attributes = True


class TrosakSaPodacima(Trosak):
    faza_naziv: Optional[str] = None
    firma_naziv: Optional[str] = None


class BudzetBase(BaseModel):
    faza_id: int
    planirani_iznos: int = 0
    napomena: Optional[str] = None


class BudzetCreate(BudzetBase):
    pass


class BudzetUpdate(BaseModel):
    planirani_iznos: Optional[int] = None
    napomena: Optional[str] = None


class Budzet(BudzetBase):
    id: int
    kreirano: datetime
    izmenjeno: datetime

    class Config:
        from_attributes = True


class RezimeFaze(BaseModel):
    faza_id: int
    faza_naziv: str
    faza_redni_broj: int
    planirani_budzet: int
    stvarni_troskovi: int
    broj_troskova: int
    procenat_iskoriscenja: float


class RezimeUkupno(BaseModel):
    ukupan_budzet: int
    ukupni_troskovi: int
    preostalo: int
    procenat_iskoriscenja: float
    po_fazama: list[RezimeFaze]