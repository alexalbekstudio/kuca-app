from sqlalchemy.orm import Session
from .models_korisnici import Korisnik
from .security import get_password_hash

def inicijalizuj_korisnike(db: Session):
    if db.query(Korisnik).count() > 0:
        return

    # Tvoji podaci
    k1 = Korisnik(
        ime="Aleksandar",
        email="alexalbekstudio.design@gmail.com",
        lozinka_hash=get_password_hash("Alex@+65!") # PROMENI OVO
    )
    # Podaci supruge
    k2 = Korisnik(
        ime="Slavica",
        email="swan.slavica@gmail.com",
        lozinka_hash=get_password_hash("Alex@+65!") # PROMENI OVO
    )
    
    db.add(k1)
    db.add(k2)
    db.commit()