from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DokumentBase(BaseModel):
    naziv: str
    opis: Optional[str] = None
    kategorija: str = "ostalo"
    faza_id: Optional[int] = None
    firma_id: Optional[int] = None
    trosak_id: Optional[int] = None
    datum_dokumenta: Optional[datetime] = None


class DokumentUpdate(BaseModel):
    naziv: Optional[str] = None
    opis: Optional[str] = None
    kategorija: Optional[str] = None
    faza_id: Optional[int] = None
    firma_id: Optional[int] = None
    trosak_id: Optional[int] = None
    datum_dokumenta: Optional[datetime] = None


class Dokument(DokumentBase):
    id: int
    originalni_naziv: str
    mime_tip: str
    velicina_bajtova: int
    ocr_status: str
    kreirano: datetime
    izmenjeno: datetime
    uneo_ime: Optional[str] = None  # <--- DODATO

    class Config:
        from_attributes = True


class DokumentSaPodacima(Dokument):
    faza_naziv: Optional[str] = None
    firma_naziv: Optional[str] = None
    trosak_opis: Optional[str] = None


class DokumentPretraga(BaseModel):
    dokument: DokumentSaPodacima
    snippet: Optional[str] = None