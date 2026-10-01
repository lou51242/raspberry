import time
import RPi.GPIO as GPIO

PIN_DATA = 1 # broche à adapter

def envoyer_signal_depart(pin):
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)
	time.sleep(0.018) # 18ms
	GPIO.output(pin, GPIO.HIGH)
	time.sleep(0.00003)
	GPIO.setup(pin, GPIO.IN)

def attendre_reponse_capteur(pin):
	while GPIO.input(pin) == GPIO.HIGH:
		pass
	while GPIO.input(pin) == GPIO.LOW:
		pass
	while GPIO.input(pin) == GPIO.HIGH:
                pass
	return True

def lire_bit(pin):
	while GPIO.input(pin) == GPIO.LOW:
		pass
	debut_haut = time.time()
	while GPIO.input(pin) == GPIO.HIGH:
		pass
	fin_haut = time.time()
	duree_haut_us = (fin_haut - debut_haut) * 1000000
	if duree_haut_us > 50:
		return 1
	else:
		return 0


def lire_trame(pin):
	GPIO.setmode(GPIO.BCM)
	envoyer_signal_depart(pin)
	if not attendre_reponse_capteur(pin):
		raise TimeoutError("Pas de réponse du capteur")

	octets = [0, 0, 0, 0, 0]
	for i in range (40):
		bit = lire_bit(pin)
		octets[i // 8] = (octets[i // 8] << 1 ) | bit

	checksum = sum(octets[0:4]) & 0xFF
	if checksum != octets[4]:
		raise ValueError("Erreur de Checksum")

	humidite = octets[0]
	temperature=octets[2]
	return temperature, humidite

if __name__ == "__main__":
	while True:
		try:
			temp, hum = lire_trame(PIN_DATA)
			print(f"Température : {temp} °C - Humidité : {hum} %")
		except (TimeoutError, ValueError) as e:
			print(f"Erreur de lecture : {e}")
		time.sleep(2)


