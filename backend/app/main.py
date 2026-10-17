from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import time
from sqlalchemy.exc import OperationalError

from .database import engine, SessionLocal, Base
from . import (
    models, models_faze, models_veze, models_troskovi,
    models_podsetnici, models_push, models_kapital, models_dokumenti, models_materijali,
)
from .init_faze import inicijalizuj_faze
from .routers import (
    firme, faze, veze, troskovi, podsetnici, push, kapital, dokumenti, materijali,
)
from .scheduler import start_scheduler

print("=== POKREĆEM KUCA APP BACKEND ===")

# Povezivanje na bazu sa ponovnim pokušajima
print("Povezujem se na bazu...")
max_retries = 5
for i in range(max_retries):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Baza je povezana!")
        break
    except Exception as e:
        print(f"⚠️ Pokušaj {i+1}/{max_retries} nije uspeo: {e}")
        time.sleep(3)

# Kreiraj tabele (ako je baza dostupna)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabele su kreirane!")
except Exception as e:
    print(f"❌ Greška pri kreiranju tabela: {e}")

# Inicijalizuj faze
try:
    db = SessionLocal()
    inicijalizuj_faze(db)
    db.close()
    print("✅ Faze su inicijalizovane!")
except Exception as e:
    print(f"❌ Greška pri inicijalizaciji faza: {e}")

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

app.include_router(firme.router)
app.include_router(faze.router)
app.include_router(veze.router)
app.include_router(troskovi.router)
app.include_router(podsetnici.router)
app.include_router(push.router)
app.include_router(kapital.router)
app.include_router(dokumenti.router)
app.include_router(materijali.router)

@app.on_event("startup")
async def startup():
    try:
        start_scheduler()
        print("✅ Scheduler pokrenut!")
    except Exception as e:
        print(f"❌ Greška sa schedulerom: {e}")

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