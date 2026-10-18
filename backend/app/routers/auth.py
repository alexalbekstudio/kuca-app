from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
from ..database import get_db
from ..models_korisnici import Korisnik
from ..security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str

class KorisnikInfo(BaseModel):
    id: int
    ime: str
    email: str

    class Config:
        from_attributes = True

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # --- PRIVREMENI TEST ---
    if form_data.username == "test@test.com" and form_data.password == "test123":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": "test@test.com"}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    # -----------------------

    user = db.query(Korisnik).filter(Korisnik.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.lozinka_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pogrešan email ili lozinka",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=KorisnikInfo)
def read_users_me(current_user: Korisnik = Depends(get_current_user)):
    return current_user