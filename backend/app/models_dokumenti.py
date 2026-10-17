from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, BigInteger
from datetime import datetime
from .database import Base


class Dokument(Base):
    """Dokument u arhivi."""
    __tablename__ = "dokumenti"

    id = Column(Integer, primary_key=True, index=True)

    naziv = Column(String(300), nullable=False)
    opis = Column(Text, nullable=True)
    kategorija = Column(String(50), nullable=False, default="ostalo")

    putanja = Column(String(500), nullable=False)
    originalni_naziv = Column(String(300), nullable=False)
    mime_tip = Column(String(100), nullable=False)
    velicina_bajtova = Column(BigInteger, nullable=False)

    ocr_tekst = Column(Text, nullable=True)
    ocr_status = Column(String(20), nullable=False, default="ceka")

    faza_id = Column(Integer, ForeignKey("faze.id", ondelete="SET NULL"), nullable=True)
    firma_id = Column(Integer, ForeignKey("firme.id", ondelete="SET NULL"), nullable=True)
    trosak_id = Column(Integer, ForeignKey("troskovi.id", ondelete="SET NULL"), nullable=True)

    datum_dokumenta = Column(DateTime, nullable=True)
    
    # Ko je uneo
    uneo_id = Column(Integer, ForeignKey("korisnici.id", ondelete="SET NULL"), nullable=True)

    kreirano = Column(DateTime, default=datetime.utcnow)
    izmenjeno = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)