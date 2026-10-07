#!/usr/bin/env python3

from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

def connexion_db():
    conn = sqlite3.connect("temperatures.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def dashboard():
    conn = connexion_db()
    # ... à compléter : récupérer, pour chaque armoire, sa dernière mesure
    # et déterminer si elle est conforme (SELECT ... ORDER BY horodatage DESC LIMIT 1)
    armoires = conn.execute("SELECT * FROM Armoire").fetchall()
    dernieres_mesures = []
    for armoire in armoires:
        mesure = conn.execute(
            "SELECT * FROM Mesure WHERE armoire_id = ? "
            "ORDER BY horodatage DESC LIMIT 1", (armoire["id"],)
        ).fetchone()
        conforme = armoire["temp_min"] <= mesure["temperature"] <= armoire["temp_max"]
        dernieres_mesures.append({
            "armoire": armoire, "mesure": mesure, "conforme": conforme
        })
    return render_template("dashboard.html", donnees=dernieres_mesures)

@app.route("/api/dernieres")
def api_dernieres():
    # ... à compléter : même logique que ci-dessus, renvoyée en JSON
    # pour un rafraîchissement AJAX côté navigateur toutes les 10 s
    pass

@app.route("/historique/<int:armoire_id>")
def historique(armoire_id):
    conn = connexion_db()
    mesures = conn.execute(
        "SELECT horodatage, temperature FROM Mesure "
        "WHERE armoire_id = ? AND horodatage >= datetime('now', '-7 days') "
        "ORDER BY horodatage", (armoire_id,)
    ).fetchall()
    return render_template("historique.html", mesures=mesures,
                           armoire_id=armoire_id)

@app.route("/affichage")
def affichage_cuisine():
    # page destinée à l'écran de cuisine, sans navigation, grand format
    return render_template("affichage_cuisine.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
