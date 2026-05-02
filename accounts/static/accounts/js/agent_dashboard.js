/* ============================================================
   static/js/agent_dashboard.js
   Logique spécifique au Tableau de Bord Agent (Maquette p.1)
   ============================================================ */

document.addEventListener('DOMContentLoaded', function() {
    
    // 1. GÉOLOCALISATION EN TEMPS RÉEL
    if ("geolocation" in navigator) {
        // Surveiller la position de l'agent
        navigator.geolocation.watchPosition(
            (position) => {
                envoyerPositionGPS(position.coords);
                document.getElementById('indicateur-gps-status').className = 'position-absolute bottom-0 end-0 p-1 bg-success border border-light rounded-circle';
            },
            (error) => {
                console.error("Erreur GPS:", error);
                document.getElementById('indicateur-gps-status').className = 'position-absolute bottom-0 end-0 p-1 bg-danger border border-light rounded-circle';
            },
            { enableHighAccuracy: true, maximumAge: 30000, timeout: 27000 }
        );
    }

    function envoyerPositionGPS(coords) {
        fetch(GPS_UPDATE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN
            },
            body: JSON.stringify({
                latitude: coords.latitude,
                longitude: coords.longitude,
                precision: coords.accuracy
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.succes) console.warn("Echec sync GPS");
        })
        .catch(err => console.error("Erreur réseau GPS:", err));
    }

    // 2. MARQUER TOUT COMME LU (Flux d'activité)
    const btnMarquerLu = document.getElementById('btn-marquer-tout-lu');
    if (btnMarquerLu) {
        btnMarquerLu.addEventListener('click', function() {
            const url = this.dataset.url;
            
            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF_TOKEN }
            })
            .then(response => response.json())
            .then(data => {
                if (data.succes) {
                    // Mettre à jour l'UI : retirer le fond coloré des items non lus
                    const items = document.querySelectorAll('#flux-activite-liste li');
                    items.forEach(item => item.classList.remove('bg-light-info'));
                    this.style.display = 'none'; // Cacher le bouton
                    window.afficherToast("Flux d'activité mis à jour", "success");
                }
            });
        });
    }

    // 3. RECHARGEMENT AUTOMATIQUE DES COMPTEURS (Optionnel)
    // On pourrait ajouter un intervalle ici pour rafraîchir les stats sans recharger la page
    setInterval(() => {
        // Logique de rafraîchissement des compteurs via AJAX si besoin
    }, 60000); // Toutes les minutes
});

/* Styles inline spécifiques pour l'aspect maquette */
const style = document.createElement('style');
style.innerHTML = `
    .bg-light-info { background-color: #f0f7ff !important; border-left: 3px solid #0d6efd; }
`;
document.head.appendChild(style);