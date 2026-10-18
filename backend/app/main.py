from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import time

from .database import engine, SessionLocal, Base
from . import (
    models, models_faze, models_veze, models_troskovi,
    models_podsetnici, models_push, models_kapital, models_dokumenti, models_materijali,
)
from .init_faze import inicijalizuj_faze
from .init_korisnici import inicijalizuj_korisnike
from .routers import (
    firme, faze, veze, troskovi, podsetnici, push, kapital, dokumenti, auth, materijali,
)
from .scheduler import start_scheduler

print("=== POKREĆEM KUCA APP BACKEND ===")

# Povezivanje na bazu
print("Povezujem se na bazu...")
Base.metadata.create_all(bind=engine)
print("✅ Tabele su kreirane!")

# Inicijalizacija faza i korisnika
db = SessionLocal()
try:
    inicijalizuj_faze(db)
    print("✅ Faze su inicijalizovane!")
    
    inicijalizuj_korisnike(db)
    print("✅ Korisnici su inicijalizovani!")
finally:
    db.close()

# 1. PRVO SE PRAVI APLIKACIJA
app = FastAPI(
    title="Kuca App API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. TEK ONDA SE DODAJU RUTERI
app.include_router(auth.router)
app.include_router(firme.router)
app.include_router(faze.router)
app.include_router(veze.router)
app.include_router(troskovi.router)
app.include_router(podsetnici.router)
app.include_router(push.router)
app.include_router(kapital.router)
app.include_router(dokumenti.router)
app.include_router(materijali.router)  # <--- SADA JE NA PRAVOM MESTU

@app.on_event("startup")
async def startup():
    start_scheduler()

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "kuca-app"}

@app.get("/api/db-check")
def db_check():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
        return {"db": "ok", "version": version}
    except Exception as e:
        return {"db": "greška", "detail": str(e)}

@app.get("/")
def read_root():
    return {"message": "Dobrodošli na Kuca App API!", "status": "aktivan"}