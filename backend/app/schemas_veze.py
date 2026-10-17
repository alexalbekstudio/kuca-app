from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FazaFirmaBase(BaseModel):
    firma_id: int
    uloga: str = "ostalo"
    napomena: Optional[str] = None
    cena: Optional[int] = None


class FazaFirmaCreate(FazaFirmaBase):
    pass


class FazaFirmaUpdate(BaseModel):
    uloga: Optional[str] = None
    napomena: Optional[str] = None
    cena: Optional[int] = None


class FazaFirma(FazaFirmaBase):
    id: int
    faza_id: int
    kreirano: datetime

    class Config:
        from_attributes = True


class FazaFirmaSaPodacima(FazaFirma):
    """Proširena verzija koja uključuje i podatke o firmi."""
    firma_naziv: str
    firma_kategorija: str
    firma_telefon: Optional[str] = None
    firma_kontakt: Optional[str] = None