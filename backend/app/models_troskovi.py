from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey
from datetime import datetime
from .database import Base


class Trosak(Base):
    """Stvarni trošak — svaka uplata, račun ili trošak vezan za fazu."""
    __tablename__ = "troskovi"

    id = Column(Integer, primary_key=True, index=True)

    faza_id = Column(Integer, ForeignKey("faze.id", ondelete="SET NULL"), nullable=True)
    firma_id = Column(Integer, ForeignKey("firme.id", ondelete="SET NULL"), nullable=True)

    opis = Column(String(300), nullable=False)
    kategorija = Column(String(50), nullable=False, default="materijal")
    iznos = Column(Integer, nullable=False)
    datum_troska = Column(Date, nullable=False)
    datum_placanja = Column(Date, nullable=True)
    status = Column(String(30), nullable=False, default="planirano")
    broj_dokumenta = Column(String(100), nullable=True)
    napomena = Column(Text, nullable=True)
    
    # Ko je uneo
    uneo_id = Column(Integer, ForeignKey("korisnici.id", ondelete="SET NULL"), nullable=True)

    kreirano = Column(DateTime, default=datetime.utcnow)
    izmenjeno = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Budzet(Base):
    """Planirani budžet po fazi."""
    __tablename__ = "budzeti"

    id = Column(Integer, primary_key=True, index=True)
    faza_id = Column(Integer, ForeignKey("faze.id", ondelete="CASCADE"), nullable=False, unique=True)
    planirani_iznos = Column(Integer, nullable=False, default=0)
    napomena = Column(Text, nullable=True)

    kreirano = Column(DateTime, default=datetime.utcnow)
    izmenjeno = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)