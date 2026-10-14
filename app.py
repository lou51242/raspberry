#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, send_file
from flask_socketio import SocketIO, emit  # Ajout des imports SocketIO
import sqlite3
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

app = Flask(__name__)
# Initialisation de SocketIO avec gestion du multithreading
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def connexion_db():
    conn = sqlite3.connect("temperatures.db")
    conn.row_factory = sqlite3.Row
    return conn

def recuperer_dernieres_mesures():
    """Fonction utilitaire pour formater les dernières données pour le Dashboard et l'API WebSocket"""
    conn = connexion_db()
    armoires = conn.execute("SELECT * FROM Armoire").fetchall()
    dernieres_mesures = []
    for armoire in armoires:
        mesure = conn.execute(
            "SELECT * FROM Mesure WHERE armoire_id = ? "
            "ORDER BY horodatage DESC LIMIT 1", (armoire["id"],)
        ).fetchone()
        
        if mesure:
            conforme = armoire["temp_min"] <= mesure["temperature"] <= armoire["temp_max"]
            mesure_data = {
                "horodatage": mesure["horodatage"],
                "temperature": mesure["temperature"],
                "humidite": mesure["humidite"]  # Aligné avec supervision.js ('humidite')
            }
        else:
            conforme = False
            mesure_data = None
            
        dernieres_mesures.append({
            "armoire": {
                "id": armoire["id"],
                "temp_min": armoire["temp_min"],
                "temp_max": armoire["temp_max"]
            },
            "mesure": mesure_data,
            "conforme": conforme
        })
    conn.close()
    return dernieres_mesures

def tache_fond_websocket():
    """Tâche qui s'exécute en continu pour pousser les mises à jour de la DB vers les navigateurs"""
    while True:
        socketio.sleep(5)  # Envoi toutes les 5 secondes
        try:
            donnees = recuperer_dernieres_mesures()
            # Envoi des données sur le canal WebSocket 'mise_a_jour_donnees'
            socketio.emit('mise_a_jour_donnees', donnees)
        except Exception as e:
            print(f"Erreur lors de l'envoi WebSocket : {e}")

# Lancement automatique de la tâche de fond à la première connexion d'un utilisateur
@socketio.on('connect')
def au_connect():
    print("Client connecté au WebSocket")

@app.route("/")
def dashboard():
    # Utilisation de la fonction utilitaire pour charger la page initiale en Jinja2
    dernieres_mesures = recuperer_dernieres_mesures()
    return render_template("dashboard.html", donnees=dernieres_mesures)

@app.route("/api/dernieres")
def api_dernieres():
    dernieres_mesures = recuperer_dernieres_mesures()
    return jsonify(dernieres_mesures)

@app.route("/historique/<int:armoire_id>")
def historique(armoire_id):
    conn = connexion_db()
    date_limite = (datetime.now() - timedelta(days=7)).isoformat()
    mesures = conn.execute(
        "SELECT horodatage, temperature FROM Mesure "
        "WHERE armoire_id = ? AND horodatage >= ? "
        "ORDER BY horodatage", (armoire_id, date_limite)
    ).fetchall()
    conn.close()
    return render_template("historique.html", mesures=mesures, armoire_id=armoire_id)

@app.route("/historique/<int:armoire_id>/pdf")
def generer_rapport_haccp(armoire_id):
    conn = connexion_db()
    armoire = conn.execute("SELECT * FROM Armoire WHERE id = ?", (armoire_id,)).fetchone()
    date_limite = (datetime.now() - timedelta(days=7)).isoformat()
    mesures = conn.execute(
        "SELECT horodatage, temperature, humidite FROM Mesure "
        "WHERE armoire_id = ? AND horodatage >= ? "
        "ORDER BY horodatage DESC", (armoire_id, date_limite)
    ).fetchall()
    
    tampon_pdf = io.BytesIO()
    doc = SimpleDocTemplate(tampon_pdf, pagesize=letter, title=f"Rapport_HACCP_Armoire_{armoire_id}")
    elements = []
    styles = getSampleStyleSheet()
    style_titre = ParagraphStyle('TitreHACCP', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#2c3e50'), spaceAfter=12)
    style_normal = styles['Normal']
    
    elements.append(Paragraph("<b>RAPPORT RÉGLEMENTAIRE DE TRAÇABILITÉ THERMIQUE (HACCP)</b>", style_titre))
    elements.append(Spacer(1, 10))
    
    info_texte = f"""
    <b>Équipement contrôlé :</b> Armoire Réfrigérée {armoire_id}<br/>
    <b>Plage de tolérance réglementaire :</b> {armoire['temp_min']} °C à {armoire['temp_max']} °C<br/>
    <b>Période du rapport :</b> 7 derniers jours<br/>
    <b>Date d'extraction du document :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}
    """
    elements.append(Paragraph(info_texte, style_normal))
    elements.append(Spacer(1, 20))
    
    donnees_tableau = [['Date et Heure', 'Température enregistrée', 'Humidité', 'Conformité']]
    for m in mesures:
        conforme = armoire['temp_min'] <= m['temperature'] <= armoire['temp_max']
        statut = "CONFORME" if conforme else "NON CONFORME"
        try:
            dt = datetime.fromisoformat(m['horodatage'])
            date_lisible = dt.strftime('%d/%m/%Y %H:%M')
        except ValueError:
            date_lisible = m['horodatage']
        donnees_tableau.append([
            date_lisible,
            f"{m['temperature']} °C",
            f"{m['humidite']}%",
            statut
        ])
        
    tableau = Table(donnees_tableau, colWidths=[150, 130, 100, 100])
    style_table = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ])
    
    for i in range(1, len(donnees_tableau)):
        if donnees_tableau[i][3] == "NON CONFORME":
            style_table.add('TEXTCOLOR', (3, i), (3, i), colors.red)
            style_table.add('FONTNAME', (3, i), (3, i), 'Helvetica-Bold')
            
    tableau.setStyle(style_table)
    elements.append(tableau)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("<b>Visa de l'autorité de contrôle (Nom, Date, Signature) :</b>", style_normal))
    elements.append(Spacer(1, 40))
    
    doc.build(elements)
    tampon_pdf.seek(0)
    conn.close()
    
    return send_file(
        tampon_pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"rapport_haccp_armoire_{armoire_id}.pdf"
    )

@app.route("/affichage")
def affichage_cuisine():
    return render_template("affichage_cuisine.html")

if __name__ == "__main__":
    # Démarrage de la tâche de fond de rafraîchissement des WebSockets
    socketio.start_background_task(tache_fond_websocket)
    # Lancement via socketio.run à la place de app.run
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
