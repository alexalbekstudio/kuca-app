from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import time

from .database import engine, SessionLocal, Base
from . import (
    models, models_faze, models_veze, models_troskovi,
    models_podsetnici, models_push, models_kapital, models_dokumenti,
)
from .init_faze import inicijalizuj_faze
from .routers import (
    firme, faze, veze, troskovi, podsetnici, push, kapital, dokumenti,
)
from .scheduler import start_scheduler

print("=== POKREĆEM KUCA APP BACKEND ===")

# Povezivanje na bazu
print("Povezujem se na bazu...")
Base.metadata.create_all(bind=engine)
print("✅ Tabele su kreirane!")

# Inicijalizacija faza
db = SessionLocal()
try:
    inicijalizuj_faze(db)
    print("✅ Faze su inicijalizovane!")
finally:
    db.close()

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