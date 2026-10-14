const socket = io();

socket.on('mise_a_jour_donnees', function(donnees) {
    console.log("Données reçues en temps réel via WebSocket :", donnees);
    
    donnees.forEach(item => {
        const ligne = document.getElementById(`armoire-${item.armoire.id}`);
        
        if (ligne && item.mesure) {
            ligne.querySelector('.temperature').textContent = `${item.mesure.temperature} °C`;
            ligne.querySelector('.humidity').textContent = `${item.mesure.humidite}%`;
            
            const celluleStatut = ligne.cells[4]; 
            
            if (item.conforme) {
                celluleStatut.innerHTML = '<span class="statut conforme">Conforme</span>';
            } else {
                celluleStatut.innerHTML = '<span class="statut non-conforme">Non conforme</span>';
            }
        }
    });
});

socket.on('connect', () => console.log("Connecté au serveur WebSocket !"));
socket.on('disconnect', () => console.log("Déconnecté du serveur WebSocket."));
