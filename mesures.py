#!/usr/bin/env python3

import sqlite3
import time
from datetime import datetime
import board
import adafruit_dht

# Configuration pour un seul capteur sur le GPIO 23
CONNEXIONS = {
    1: 23  # armoire_id -> broche GPIO
}

# Initialisation unique du capteur via la bibliothèque officielle
capteur_dht = adafruit_dht.DHT11(board.D23)

def lire_trame(pin_ignoree):
    """Lit les données du capteur de manière fiable via Adafruit."""
    temperature = capteur_dht.temperature
    humidite = capteur_dht.humidity

    if temperature is not None and humidite is not None:
        return temperature, humidite
    raise RuntimeError("Données lues vides")

def enregistrer_mesure(connexion, armoire_id, temperature, humidite):
    connexion.execute(
        "INSERT INTO Mesure (armoire_id, horodatage, temperature, humidite) "
        "VALUES (?, ?, ?, ?)",
        (armoire_id, datetime.now().isoformat(), temperature, humidite)
    )
    connexion.commit()

def boucle_mesure():

    connexion = sqlite3.connect("/home/pi/lou/supervision/temperatures.db")

    connexion.execute("""
        CREATE TABLE IF NOT EXISTS Mesure (
            armoire_id INTEGER,
            horodatage TEXT,
            temperature REAL,
            humidite REAL
        )
    """)

    print("=== Démarrage de la boucle de supervision (Période: 10s) ===")
    while True:
        debut = time.time()
        for armoire_id, pin in CONNEXIONS.items():
            try:
                temperature, humidite = lire_trame(pin)
                enregistrer_mesure(connexion, armoire_id, temperature, humidite)
                print(f"Enregistrement Armoire {armoire_id} -> {temperature}°C | {humidite}%")
            except Exception as e:
                pass

        duree_ecoulee = time.time() - debut
        temps_restant = 10.0 - duree_ecoulee

        if temps_restant > 0:
            time.sleep(temps_restant)

if __name__ == "__main__":
    try:
        boucle_mesure()
    except KeyboardInterrupt:
        capteur_dht.exit()
        print("\nProgramme arrêté.")
