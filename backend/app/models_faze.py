from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from datetime import datetime
from .database import Base

class Faza(Base):
    __tablename__ = "faze"

    id = Column(Integer, primary_key=True, index=True)

    # Redni broj faze (1-8)
    redni_broj = Column(Integer, nullable=False, unique=True)

    # Naziv i opis
    naziv = Column(String(200), nullable=False)
    opis = Column(Text, nullable=True)

    # Status: "nije_početo", "u_toku", "završeno", "blokirano"
    status = Column(String(30), nullable=False, default="nije_početo")

    # Rokovi
    planirani_pocetak = Column(Date, nullable=True)
    planirani_kraj = Column(Date, nullable=True)
    stvarni_pocetak = Column(Date, nullable=True)
    stvarni_kraj = Column(Date, nullable=True)

    # Čeklista dokumenata — čuvamo kao JSON string
    # Primer: [{"naziv": "List nepokretnosti", "zavrseno": true}, ...]
    dokumenti = Column(Text, nullable=True, default="[]")

    # Beleške
    napomena = Column(Text, nullable=True)

    # Automatski timestamp
    kreirano = Column(DateTime, default=datetime.utcnow)
    izmenjeno = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)