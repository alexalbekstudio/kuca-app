import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import mimetypes


def _ocr_slika(putanja: str) -> str:
    """OCR za sliku."""
    try:
        img = Image.open(putanja)
        # Ako je slika prevelika, smanji (brže)
        if max(img.size) > 3000:
            img.thumbnail((3000, 3000), Image.LANCZOS)

        # OCR sa srpskim + engleskim
        tekst = pytesseract.image_to_string(
            img,
            lang="srp+eng",
            config="--psm 3",
        )
        return tekst.strip()
    except Exception as e:
        print(f"[OCR] Greška pri obradi slike: {e}")
        return ""


def _ocr_pdf(putanja: str) -> str:
    """OCR za PDF — konvertuje u slike pa OCR."""
    try:
        # Konvertuj PDF u slike (300 DPI)
        slike = convert_from_path(putanja, dpi=200, first_page=1, last_page=50)
        delovi = []
        for i, slika in enumerate(slike):
            print(f"[OCR] PDF strana {i+1}/{len(slike)}...")
            tekst = pytesseract.image_to_string(slika, lang="srp+eng", config="--psm 3")
            if tekst.strip():
                delovi.append(f"--- Strana {i+1} ---\n{tekst.strip()}")
        return "\n\n".join(delovi)
    except Exception as e:
        print(f"[OCR] Greška pri obradi PDF-a: {e}")
        return ""


def izvrsi_ocr(putanja: str, mime_tip: str) -> str:
    """Pokreće OCR na osnovu tipa fajla."""
    if mime_tip.startswith("image/"):
        return _ocr_slika(putanja)
    elif mime_tip == "application/pdf":
        return _ocr_pdf(putanja)
    else:
        return ""


def proceni_mime_tip(putanja: str) -> str:
    """Određuje MIME tip fajla na osnovu ekstenzije i sadržaja."""
    mime, _ = mimetypes.guess_type(putanja)
    return mime or "application/octet-stream"