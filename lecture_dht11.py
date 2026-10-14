#!/usr/bin/env python3

import time
import board
import adafruit_dht

PIN_DATA = 23
capteur_dht = adafruit_dht.DHT11(board.D23)

def lire_trame_avec_retry(max_retries=3, delai_retry=2.1):
    for tentative in range(1, max_retries + 1):
        try:
            temperature = capteur_dht.temperature
            humidite = capteur_dht.humidity
            if temperature is not None and humidite is not None:
                return temperature, humidite
        except RuntimeError:
            if tentative < max_retries:
                print(f"[Alerte] Échec lecture ({tentative}/{max_retries}). Nouvelle tentative dans {delai_retry}s...")
                time.sleep(delai_retry)
            else:
                raise RuntimeError(f"Capteur indisponible après {max_retries} tentatives.")

if __name__ == '__main__':
    print("=== Stratégie de Retry ===")
    try:
        while True:
            try:
                temp, hum = lire_trame_avec_retry(max_retries=3, delai_retry=2.1)
                print(f"Température : {temp:.1f} °C - Humidité : {hum}%")
            except RuntimeError as e:
                print(f"Erreur Critique : {e}")
            time.sleep(5.0)
    except KeyboardInterrupt:
        pass
    finally:
        capteur_dht.exit()
        print("\nFin du programme")
