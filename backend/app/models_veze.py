from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from .database import Base


class FazaFirma(Base):
    """Veza između faze i firme — ko je angažovan za koju fazu."""
    __tablename__ = "faza_firma"

    id = Column(Integer, primary_key=True, index=True)

    faza_id = Column(Integer, ForeignKey("faze.id", ondelete="CASCADE"), nullable=False)
    firma_id = Column(Integer, ForeignKey("firme.id", ondelete="CASCADE"), nullable=False)

    # Uloga u ovoj fazi
    uloga = Column(String(50), nullable=False, default="ostalo")

    # Napomena specifična za ovu fazu i firmu
    napomena = Column(Text, nullable=True)

    # Dogovorena cena (opciono)
    cena = Column(Integer, nullable=True)

    kreirano = Column(DateTime, default=datetime.utcnow)