from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import re

# Uzimamo URL iz okruženja
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL nije postavljen!")

# Čistimo URL od bilo kakvih navodnika ili razmaka
DATABASE_URL = DATABASE_URL.strip().strip('"').strip("'")

# Prisiljavamo ispravan drajver za SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Ispisujemo URL (bez lozinke) da vidimo šta se tačno dešava
bez_lozinke = re.sub(r':[^:@]+@', ':***@', DATABASE_URL)
print(f"🔗 Povezujem se na bazu: {bez_lozinke}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()