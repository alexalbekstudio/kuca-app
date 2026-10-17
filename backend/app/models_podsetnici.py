from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Text, ForeignKey, Boolean
from datetime import datetime
from .database import Base


class Podsetnik(Base):
    """Podsetnik — obaveza sa rokom."""
    __tablename__ = "podsetnici"

    id = Column(Integer, primary_key=True, index=True)

    # Osnovno
    naslov = Column(String(200), nullable=False)
    opis = Column(Text, nullable=True)

    # Veze (opciono)
    faza_id = Column(Integer, ForeignKey("faze.id", ondelete="SET NULL"), nullable=True)
    firma_id = Column(Integer, ForeignKey("firme.id", ondelete="SET NULL"), nullable=True)

    # Rok
    datum_dospeca = Column(Date, nullable=False)
    vreme_dospeca = Column(Time, nullable=True)  # opciono, za precizne sate

    # Prioritet: "nisko", "srednje", "visoko", "hitno"
    prioritet = Column(String(20), nullable=False, default="srednje")

    # Kategorija: "zakonski", "ugovor", "licenca", "placanje", "opste"
    kategorija = Column(String(30), nullable=False, default="opste")

    # Status
    zavrseno = Column(Boolean, nullable=False, default=False)
    datum_zavrsetka = Column(DateTime, nullable=True)

    # Da li je podsetnik automatski generisan (npr. iz zakona)
    automatski = Column(Boolean, nullable=False, default=False)

    # Koliko dana pre dospeća da se prikaže kao "uskoro"
    podseti_dana_pre = Column(Integer, nullable=False, default=3)

    kreirano = Column(DateTime, default=datetime.utcnow)
    izmenjeno = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)