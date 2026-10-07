#!/usr/bin/env python3

import sqlite3
import time
from datetime import datetime
from lecture_dht11 import lire_trame

CONNEXIONS = {
    1: 4, 2: 17, 3: 27, 4: 22, 5: 23 # armoire_id -> broche GPIO
}

def enregistrer_mesure(connexion, armoire_id, temperature, humidite):
    connexion.execute(
        "INSERT INTO Mesure (armoire_id, horodatage, temperature, humidite) "
        "VALUES (?, ?, ?, ?)",
        (armoire_id, datetime.now().isoformat(), temperature, humidite)
    )
    connexion.commit()

def boucle_mesure():
    connexion = sqlite3.connect("temperatures.db")
    while True:
        debut = time.time()
        for armoire_id, pin in CONNEXIONS.items():
            try:
                temperature, humidite = lire_trame(pin)
                enregistrer_mesure(connexion, armoire_id, temperature,
                                   humidite)
            except (TimeoutError, ValueError) as e:
                print(f"Armoire {armoire_id} : erreur de lecture ({e})")
        # ... à compléter : attendre le temps restant pour respecter la période de 10 s
        duree_ecoulee = ...
        time.sleep(...)

if __name__ == "__main__":
    boucle_mesure()
