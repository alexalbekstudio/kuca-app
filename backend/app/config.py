import os


# Email podešavanja
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "alexalbekstudio.design@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "stcy zhsb nyhp ujzy")

# Više primalaca — razdvojeni zarezom
# Primer: "prvi@gmail.com,drugi@gmail.com"
_email_primaoci_raw = os.getenv("EMAIL_PRIMALAC", "alexalbekstudio.design@gmail.com, swan.slavica@gmail.com")
EMAIL_PRIMAOCI = [e.strip() for e in _email_primaoci_raw.split(",") if e.strip()]

# VAPID ključevi za Web Push
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "Db0L88nqFWQMTghZUi-CFCA3SHpIRKxir3CysNImjNE")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "BCea4DjU1AiOXw9u_g-AJ-yp7hoZyeZWIYHGEZEgDeJoYGYPrzzlkYHy1x52qOSr4lrcKTDj4pNucFPL-Eg1C_g")
VAPID_CLAIM_EMAIL = os.getenv("VAPID_CLAIM_EMAIL", "mailto:alexalbekstudio.design@gmail.com")