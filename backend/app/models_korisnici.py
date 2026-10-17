from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base


class Korisnik(Base):
    __tablename__ = "korisnici"

    id = Column(Integer, primary_key=True, index=True)
    ime = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    lozinka_hash = Column(String(200), nullable=False)
    kreirano = Column(DateTime, default=datetime.utcnow)