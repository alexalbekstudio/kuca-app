from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database import get_db
from ..models_push import PushPretplata
from ..notifikacije import proveri_podsetnike
from ..security import get_current_user

router = APIRouter(prefix="/api/push", tags=["push"], dependencies=[Depends(get_current_user)])


class PretplataCreate(BaseModel):
    endpoint: str
    p256dh: str
    auth: str
    user_agent: Optional[str] = None


@router.get("/vapid-public-key")
def vapid_public_key():
    """Vraća javni VAPID ključ za frontend."""
    from ..config import VAPID_PUBLIC_KEY
    if not VAPID_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="VAPID ključevi nisu konfigurisani")
    return {"publicKey": VAPID_PUBLIC_KEY}


@router.post("/pretplati-se", status_code=201)
def pretplati_se(pretplata: PretplataCreate, db: Session = Depends(get_db)):
    """Registruje novu push pretplatu."""
    # Ako već postoji sa istim endpoint-om, ažuriraj
    postoji = db.query(PushPretplata).filter(PushPretplata.endpoint == pretplata.endpoint).first()

    if postoji:
        postoji.p256dh = pretplata.p256dh
        postoji.auth = pretplata.auth
        postoji.user_agent = pretplata.user_agent
        postoji.aktivan = 1
        db.commit()
        return {"status": "ažurirano", "id": postoji.id}

    nova = PushPretplata(**pretplata.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return {"status": "kreirano", "id": nova.id}


@router.delete("/pretplati-se", status_code=204)
def odjavi_se(endpoint: str, db: Session = Depends(get_db)):
    """Briše pretplatu."""
    p = db.query(PushPretplata).filter(PushPretplata.endpoint == endpoint).first()
    if p:
        db.delete(p)
        db.commit()


@router.post("/test")
def test_notifikacije(db: Session = Depends(get_db)):
    """Ručno pokreće proveru podsetnika — za testiranje."""
    proveri_podsetnike(db)
    return {"status": "poslato"}


@router.get("/preplate/")
def lista_preplata(db: Session = Depends(get_db)):
    """Lista svih pretplata (za debug)."""
    pretplate = db.query(PushPretplata).all()
    return [
        {
            "id": p.id,
            "aktivan": p.aktivan,
            "user_agent": p.user_agent,
            "kreirano": p.kreirano,
        }
        for p in pretplate
    ]