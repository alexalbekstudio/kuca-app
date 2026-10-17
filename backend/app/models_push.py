from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .database import Base


class PushPretplata(Base):
    """Pretplata na Web Push notifikacije."""
    __tablename__ = "push_pretplate"

    id = Column(Integer, primary_key=True, index=True)

    # Podaci iz browsera
    endpoint = Column(Text, nullable=False, unique=True)
    p256dh = Column(String(200), nullable=False)
    auth = Column(String(100), nullable=False)

    # Info o uređaju (opciono)
    user_agent = Column(String(300), nullable=True)

    # Da li je aktivna (možeš isključiti bez brisanja)
    aktivan = Column(Integer, nullable=False, default=1)

    kreirano = Column(DateTime, default=datetime.utcnow)