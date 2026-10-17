FROM python:3.12-slim

# Sistemske zavisnosti
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-srp \
    tesseract-ocr-eng \
    tesseract-ocr-hrv \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Putanje sada kreću od backend/ jer Railway gradi iz korena projekta
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

# OVO JE KLJUČNO ZA RAILWAY
EXPOSE 8000

# Railway ne koristi reload, već obično pokretanje
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]