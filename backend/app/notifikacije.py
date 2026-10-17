import smtplib
import json
from email.message import EmailMessage
from datetime import date

from sqlalchemy.orm import Session
from pywebpush import webpush, WebPushException

from . import config
from .models_podsetnici import Podsetnik
from .models_push import PushPretplata


# ===== EMAIL =====

def posalji_email(naslov: str, telo: str):
    """Šalje email na sve primaoce preko Gmail SMTP-a."""
    print(f"[EMAIL] Pokušavam da pošaljem: {naslov}")
    print(f"[EMAIL] SMTP_USER: {config.SMTP_USER}")
    print(f"[EMAIL] SMTP_PASSWORD dužina: {len(config.SMTP_PASSWORD) if config.SMTP_PASSWORD else 0}")
    print(f"[EMAIL] Primaoci: {config.EMAIL_PRIMAOCI}")

    if not config.SMTP_USER:
        print("[EMAIL] ❌ SMTP_USER nije konfigurisan")
        return False

    if not config.SMTP_PASSWORD:
        print("[EMAIL] ❌ SMTP_PASSWORD nije konfigurisan")
        return False

    if not config.EMAIL_PRIMAOCI:
        print("[EMAIL] ❌ Nema primalaca")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = naslov
        msg["From"] = config.SMTP_USER
        msg["To"] = ", ".join(config.EMAIL_PRIMAOCI)
        msg.set_content(telo)

        print(f"[EMAIL] Povezujem se na {config.SMTP_HOST}:{config.SMTP_PORT}...")
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as server:
            server.set_debuglevel(0)
            print("[EMAIL] STARTTLS...")
            server.starttls()
            print("[EMAIL] Login...")
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            print("[EMAIL] Send...")
            server.send_message(msg)

        print(f"[EMAIL] ✅ POSLATO na {len(config.EMAIL_PRIMAOCI)} primalaca")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL] ❌ AUTH GREŠKA: {e}")
        print("[EMAIL] Proveri App Password — mora biti 16 karaktera bez razmaka!")
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL] ❌ SMTP GREŠKA: {e}")
        return False
    except Exception as e:
        print(f"[EMAIL] ❌ OPŠTA GREŠKA: {type(e).__name__}: {e}")
        return False


# ===== WEB PUSH =====

def posalji_push(db: Session, naslov: str, telo: str, url: str = "/"):
    """Šalje push notifikaciju svim aktivnim pretplatama."""
    print(f"[PUSH] Pokušavam: {naslov}")

    if not config.VAPID_PRIVATE_KEY:
        print("[PUSH] ⚠️ VAPID_PRIVATE_KEY nije konfigurisan — preskačem")
        return 0

    pretplate = db.query(PushPretplata).filter(PushPretplata.aktivan == 1).all()
    print(f"[PUSH] Aktivnih pretplata: {len(pretplate)}")

    if not pretplate:
        print("[PUSH] Nema pretplata")
        return 0

    payload = json.dumps({
        "title": naslov,
        "body": telo,
        "url": url,
    })

    uspesno = 0
    for p in pretplate:
        try:
            webpush(
                subscription_info={
                    "endpoint": p.endpoint,
                    "keys": {"p256dh": p.p256dh, "auth": p.auth},
                },
                data=payload,
                vapid_private_key=config.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": config.VAPID_CLAIM_EMAIL},
            )
            uspesno += 1
            print(f"[PUSH] ✅ Poslato na pretplatu {p.id}")
        except WebPushException as e:
            print(f"[PUSH] ❌ Pretplata {p.id} neuspešna: {e}")
            if e.response and e.response.status_code == 410:
                p.aktivan = 0
                db.commit()

    print(f"[PUSH] Ukupno poslato: {uspesno}/{len(pretplate)}")
    return uspesno


# ===== PROVERA PODSETNIKA =====

def proveri_podsetnike(db: Session):
    """Proverava podsetnike i šalje notifikacije."""
    print("[PROVERA] Pokrećem proveru podsetnika...")
    danas = date.today()

    podsetnici = (
        db.query(Podsetnik)
        .filter(Podsetnik.zavrseno == False)  # noqa: E712
        .filter(Podsetnik.datum_dospeca <= danas)
        .all()
    )

    print(f"[PROVERA] Pronađeno {len(podsetnici)} podsetnika za danas ili ranije")

    # Uvek šalji email, čak i ako nema podsetnika (za test)
    if not podsetnici:
        naslov = "🧪 Test — Kuca App"
        telo = "Ovo je test email. Ako si ga dobio, email notifikacije rade!\n\nTrenutno nema aktivnih podsetnika."
    else:
        linije = []
        for p in podsetnici:
            dani = (p.datum_dospeca - danas).days
            if dani < 0:
                status = f"⚠️ KASNI {abs(dani)} dana"
            elif dani == 0:
                status = "📌 DANAS"
            else:
                status = f"za {dani} dana"
            linije.append(f"• [{status}] {p.naslov}")

        naslov = f"⏰ Podsetnici za danas ({len(podsetnici)})"
        telo = "\n".join(linije)
        telo += "\n\nOtvori aplikaciju: http://localhost:8080"

    posalji_email(naslov, telo)
    posalji_push(db, naslov, telo)
    print("[PROVERA] Završeno")