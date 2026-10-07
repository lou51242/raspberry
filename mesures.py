#!/usr/bin/env python3

import sqlite3
import time
from datetime import datetime
from mesures import lire_trame

# Modifié pour n'utiliser qu'un seul capteur pour le moment (ex: armoire 1 sur le GPIO 23)
CONNEXIONS = {
    1: 23  # armoire_id -> broche GPIO
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

        duree_ecoulee = time.time() - debut

        temps_restant = 10.0 - duree_ecoulee

        if temps_restant > 0:
            time.sleep(temps_restant)

if __name__ == "__main__":
    boucle_mesure()
