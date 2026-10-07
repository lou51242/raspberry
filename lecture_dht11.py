#!/usr/bin/env python3

import time
import board
import adafruit_dht

PIN_DATA = 23

# Initialisation du capteur
capteur_dht = adafruit_dht.DHT11(board.D23)

def lire_trame_avec_retry(max_retries=3, delai_retry=2.1):
    """
    Tente de lire le capteur. En cas d'échec, applique une stratégie 
    de nouvelle tentative (retry) jusqu'à max_retries.
    """
    for tentative in range(1, max_retries + 1):
        try:
            temperature = capteur_dht.temperature
            humidite = capteur_dht.humidity

            if temperature is not None and humidite is not None:
                return temperature, humidite

        except RuntimeError as e:
            # Si on a encore des essais disponibles, on attend et on boucle
            if tentative < max_retries:
                print(f"  [Alerte] Échec lecture ({tentative}/{max_retries}). Nouvelle tentative dans {delai_retry}s...")
                time.sleep(delai_retry)
            else:
                # Plus d'essais dispo : on transmet l'erreur finale
                raise RuntimeError(f"Capteur indisponible après {max_retries} tentatives.")

if __name__ == "__main__":
    print("=== Stratégie de Retry ===")
    try:
        while True:
            try:
                # Appel de la fonction robuste
                temp, hum = lire_trame_avec_retry(max_retries=3, delai_retry=2.1)
                print(f"Température : {temp:.1f} °C - Humidité : {hum}%")
            except RuntimeError as e:
                print(f"Erreur Critique : {e}")

            # Temps d'attente normal entre deux cycles de supervision
            time.sleep(5.0)

    except KeyboardInterrupt:
        capteur_dht.exit()
        print("\nFin du programme")
