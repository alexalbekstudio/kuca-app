from sqlalchemy.orm import Session
from .models_faze import Faza


# Definicija 8 faza sa čeklistama dokumenata
FAZE_DEFINICIJE = [
    {
        "redni_broj": 1,
        "naziv": "Provera parcele i identiteta",
        "opis": "Katastarska parcela, vlasništvo, tereti, pristup.",
        "dokumenti": [
            {"naziv": "List nepokretnosti", "zavrseno": False},
            {"naziv": "Katastarski plan", "zavrseno": False},
            {"naziv": "Provera tereta", "zavrseno": False},
            {"naziv": "Provera pristupa parceli", "zavrseno": False},
        ],
    },
    {
        "redni_broj": 2,
        "naziv": "Planska pravila",
        "opis": "Namena, index zauzetosti, gabariti, spratnost.",
        "dokumenti": [
            {"naziv": "Izvod iz važećeg planskog dokumenta", "zavrseno": False},
            {"naziv": "Provera namene parcele", "zavrseno": False},
            {"naziv": "Provera gabarita i spratnosti", "zavrseno": False},
        ],
    },
    {
        "redni_broj": 3,
        "naziv": "Geodetski i geotehnički podaci",
        "opis": "Geodetski snimak i geotehnički izveštaj.",
        "dokumenti": [
            {"naziv": "Geodetski snimak parcele", "zavrseno": False},
            {"naziv": "Geotehnički izveštaj (ispitivanje tla)", "zavrseno": False},
        ],
    },
    {
        "redni_broj": 4,
        "naziv": "Idejno rešenje",
        "opis": "Idejno rešenje montažne kuće usklađeno sa parcelom.",
        "dokumenti": [
            {"naziv": "Idejno rešenje", "zavrseno": False},
            {"naziv": "Potvrda o usklađenosti sa parcelom", "zavrseno": False},
        ],
    },
    {
        "redni_broj": 5,
        "naziv": "Lokacijski uslovi",
        "opis": "Urbanistički, tehnički i drugi uslovi. Preduslov za glavni projekat.",
        "dokumenti": [
            {"naziv": "Zahtev za lokacijske uslove", "zavrseno": False},
            {"naziv": "Rešenje o lokacijskim uslovima", "zavrseno": False},
        ],
    },
    {
        "redni_broj": 6,
        "naziv": "Projekat i građevinska dozvola",
        "opis": "Glavni projekat i dobijanje građevinske dozvole.",
        "dokumenti": [
            {"naziv": "Glavni projekat", "zavrseno": False},
            {"naziv": "Revizija projekta", "zavrseno": False},
            {"naziv": "Zahtev za građevinsku dozvolu", "zavrseno": False},
            {"naziv": "Građevinska dozvola", "zavrseno": False},
        ],
    },
    {
        "redni_broj": 7,
        "naziv": "Prijava radova i gradnja",
        "opis": "Prijava radova najmanje 8 dana pre početka. Izjave posle temelja i konstrukcije.",
        "dokumenti": [
            {"naziv": "Prijava radova (CIS)", "zavrseno": False},
            {"naziv": "Ugovor sa izvođačem", "zavrseno": False},
            {"naziv": "Ugovor o nadzoru", "zavrseno": False},
            {"naziv": "Izjava posle temelja + geodetski snimak", "zavrseno": False},
            {"naziv": "Izjava posle konstrukcije", "zavrseno": False},
            {"naziv": "Građevinski dnevnik", "zavrseno": False},
        ],
    },
    {
        "redni_broj": 8,
        "naziv": "Tehnički pregled i upotrebna dozvola",
        "opis": "Finalni pregled i dobijanje upotrebne dozvole.",
        "dokumenti": [
            {"naziv": "Zahtev za tehnički pregled", "zavrseno": False},
            {"naziv": "Zapisnik o tehničkom pregledu", "zavrseno": False},
            {"naziv": "Upotrebna dozvola", "zavrseno": False},
        ],
    },
]


def inicijalizuj_faze(db: Session):
    """Kreira 8 faza ako baza još nema nijednu fazu."""
    if db.query(Faza).count() > 0:
        return  # već inicijalizovano

    import json
    for def_f in FAZE_DEFINICIJE:
        faza = Faza(
            redni_broj=def_f["redni_broj"],
            naziv=def_f["naziv"],
            opis=def_f["opis"],
            dokumenti=json.dumps(def_f["dokumenti"]),
            status="nije_početo",
        )
        db.add(faza)
    db.commit()