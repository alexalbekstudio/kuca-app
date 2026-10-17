from sqlalchemy import Column, Integer, String, DateTime, Date, Text
from datetime import datetime
from .database import Base


class Kapital(Base):
    """Kapital — izvor finansiranja (ušteđevina, kredit, pomoć...)."""
    __tablename__ = "kapital"

    id = Column(Integer, primary_key=True, index=True)

    # Naziv izvora
    naziv = Column(String(200), nullable=False)  # npr. "Ušteđevina", "Kredit banke", "Pomoć roditelja"

    # Iznos
    iznos = Column(Integer, nullable=False)  # u dinarima

    # Kategorija: "usteda", "kredit", "pomoc", "prodaja", "ostalo"
    kategorija = Column(String(50), nullable=False, default="usteda")

    # Datum kada je kapital dostupan
    datum = Column(Date, nullable=False)

    # Napomena
    napomena = Column(Text, nullable=True)

    kreirano = Column(DateTime, default=datetime.utcnow)
    izmenjeno = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)