from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Date
from datetime import datetime
from .database import Base


class Materijal(Base):
    __tablename__ = "materijali"

    id = Column(Integer, primary_key=True, index=True)
    naziv = Column(String(200), nullable=False, index=True)
    jedinica = Column(String(50), nullable=False, default="kom")  # npr. m3, kg, kom, m2
    kategorija = Column(String(100), nullable=True)  # npr. "Beton", "Zidarski", "Stolarija"
    opis = Column(Text, nullable=True)

    # Ko je uneo
    uneo_id = Column(Integer, ForeignKey("korisnici.id", ondelete="SET NULL"), nullable=True)

    kreirano = Column(DateTime, default=datetime.utcnow)
    izmenjeno = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Ponuda(Base):
    __tablename__ = "ponude"

    id = Column(Integer, primary_key=True, index=True)
    materijal_id = Column(Integer, ForeignKey("materijali.id", ondelete="CASCADE"), nullable=False)
    firma_id = Column(Integer, ForeignKey("firme.id", ondelete="SET NULL"), nullable=True)

    cena = Column(Float, nullable=False)  # cena po jedinici mere
    datum_ponude = Column(Date, nullable=False)
    napomena = Column(Text, nullable=True)
    rok_isporuke = Column(String(100), nullable=True)  # npr. "7 dana"

    # Ko je uneo
    uneo_id = Column(Integer, ForeignKey("korisnici.id", ondelete="SET NULL"), nullable=True)

    kreirano = Column(DateTime, default=datetime.utcnow)