// Fonction qui interroge l'API et met à jour le tableau HTML
function mettreAJourDashboard() {
    // 1. Interrogation de l'API /api/dernieres
    fetch('/api/dernieres')
        .then(response => {
            if (!response.ok) {
                throw new Error("Erreur réseau lors de la récupération des données");
            }
            return response.json();
        })
        .then(donnees => {
            // 2. Parcours des données reçues pour mettre à jour chaque ligne du tableau
            donnees.forEach(item => {
                // On récupère la ligne de l'armoire grâce à son ID unique
                const ligne = document.getElementById(`armoire-${item.armoire.id}`);
                
                if (ligne && item.mesure) {
                    // Mise à jour du texte de la température et de l'humidité
                    ligne.querySelector('.temperature').textContent = `${item.mesure.temperature} °C`;
                    ligne.querySelector('.humidity').textContent = `${item.mesure.humidite}%`;
                    
                    // Récupération de la cellule du statut (5e colonne, index 4)
                    const celluleStatut = ligne.cells[4]; 
                    
                    // Mise à jour dynamique du badge de conformité
                    if (item.conforme) {
                        celluleStatut.innerHTML = '<span class="statut conforme">Conforme</span>';
                    } else {
                        celluleStatut.innerHTML = '<span class="statut non-conforme">Non conforme</span>';
                    }
                }
            });
        })
        .catch(error => console.error("Erreur lors du rafraîchissement automatique :", error));
}

// 3. Lancement de la fonction toutes les 10 secondes (10000 millisecondes)
setInterval(mettreAJourDashboard, 10000);
