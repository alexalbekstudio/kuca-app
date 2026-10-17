from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List


class PonudaBase(BaseModel):
    materijal_id: int
    firma_id: Optional[int] = None
    cena: float
    datum_ponude: date
    napomena: Optional[str] = None
    rok_isporuke: Optional[str] = None


class PonudaCreate(PonudaBase):
    pass


class Ponuda(PonudaBase):
    id: int
    kreirano: datetime
    firma_naziv: Optional[str] = None
    uneo_ime: Optional[str] = None

    class Config:
        from_attributes = True


class MaterijalBase(BaseModel):
    naziv: str
    jedinica: str = "kom"
    kategorija: Optional[str] = None
    opis: Optional[str] = None


class MaterijalCreate(MaterijalBase):
    pass


class Materijal(MaterijalBase):
    id: int
    kreirano: datetime
    uneo_ime: Optional[str] = None

    class Config:
        from_attributes = True


class MaterijalSaPonudama(Materijal):
    ponude: List[Ponuda] = []
    najbolja_cena: Optional[float] = None
    najbolja_firma: Optional[str] = None