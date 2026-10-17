from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from datetime import datetime
from .database import Base


class Firma(Base):
    __tablename__ = "firme"

    id = Column(Integer, primary_key=True, index=True)

    # Osnovni podaci
    naziv = Column(String(200), nullable=False)
    pib = Column(String(20), nullable=True)
    adresa_sedista = Column(String(300), nullable=True)
    adresa_proizvodnje = Column(String(300), nullable=True)

    # Kontakt
    kontakt_osoba = Column(String(100), nullable=True)
    telefon = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)

    # Kategorija
    kategorija = Column(String(50), nullable=False, default="izvođač")

    # Lokacija
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    grad = Column(String(100), nullable=True)
    postanski_broj = Column(String(10), nullable=True)

    # Licenca i status
    broj_licence = Column(String(50), nullable=True)
    licenca_vazi_do = Column(DateTime, nullable=True)
    verifikovano = Column(String(20), default="neverifikovano")

    # Napomene
    napomena = Column(Text, nullable=True)
    ocena = Column(Integer, nullable=True)  # 1-5
    beleške_saradnje = Column(Text, nullable=True)
    
    # Ko je uneo
    uneo_id = Column(Integer, ForeignKey("korisnici.id", ondelete="SET NULL"), nullable=True)

    # Automatski timestamp
    kreirano = Column(DateTime, default=datetime.utcnow)
    izmenjeno = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)