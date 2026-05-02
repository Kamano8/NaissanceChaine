// ============================================================
// NaissanceChain — JavaScript Tableau de bord Agent
// Géolocalisation GPS + Synchronisation blockchain + Flux
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

    // =========================================================
    // GÉOLOCALISATION GPS
    // Récupère la position réelle et l'envoie au serveur
    // =========================================================
    const gpsTexte  = document.getElementById('gpsTexte');
    const gpsStatut = document.getElementById('gpsStatut');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
                   || getCookie('csrftoken');

    function mettreAJourGPS() {
        if (!navigator.geolocation) {
            if (gpsTexte) gpsTexte.textContent = 'GPS : Non disponible';
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat       = position.coords.latitude.toFixed(4);
                const lon       = position.coords.longitude.toFixed(4);
                const precision = Math.round(position.coords.accuracy);

                // Mettre à jour l'affichage
                if (gpsTexte) {
                    gpsTexte.textContent = `GPS : Précis (${precision}m)`;
                }

                // Envoyer au serveur Django via AJAX
                fetch('/agents/api/gps/', {
                    method:  'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken':  csrfToken,
                    },
                    body: JSON.stringify({
                        latitude:  position.coords.latitude,
                        longitude: position.coords.longitude,
                        precision: precision,
                    }),
                })
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    if (!data.succes) {
                        console.warn('Échec mise à jour GPS :', data.erreur);
                    }
                })
                .catch(function (err) {
                    console.warn('Erreur réseau GPS :', err);
                });
            },
            function (erreur) {
                // L'utilisateur a refusé ou GPS indisponible
                if (gpsTexte) gpsTexte.textContent = 'GPS : Signal faible';
                console.warn('Erreur GPS :', erreur.message);
            },
            {
                enableHighAccuracy: true,
                timeout:            10000,
                maximumAge:         60000,
            }
        );
    }

    // Lancement immédiat + toutes les 2 minutes
    mettreAJourGPS();
    setInterval(mettreAJourGPS, 120000);


    // =========================================================
    // MARQUER LE FLUX COMME LU
    // =========================================================
    const btnMarquerLu = document.getElementById('btnMarquerLu');

    if (btnMarquerLu) {
        btnMarquerLu.addEventListener('click', function () {
            fetch('/agents/api/flux-lu/', {
                method:  'POST',
                headers: { 'X-CSRFToken': csrfToken },
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.succes) {
                    // Supprimer la bordure bleue des événements non lus
                    document.querySelectorAll('.nc-flux-non-lu').forEach(function (el) {
                        el.classList.remove('nc-flux-non-lu');
                    });
                    btnMarquerLu.textContent = 'Tout lu ✓';
                    btnMarquerLu.style.color = '#0d9e6e';
                }
            })
            .catch(function (err) {
                console.warn('Erreur marquer lu :', err);
            });
        });
    }


    // =========================================================
    // MISE À JOUR EN TEMPS RÉEL DES COMPTEURS
    // Recharge la page toutes les 60 secondes pour les live data
    // =========================================================
    setTimeout(function () {
        window.location.reload();
    }, 60000);


    // =========================================================
    // UTILITAIRE : Lire un cookie (pour le CSRF token)
    // =========================================================
    function getCookie(nom) {
        let cookieVal = null;
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach(function (cookie) {
                const c = cookie.trim();
                if (c.startsWith(nom + '=')) {
                    cookieVal = decodeURIComponent(c.substring(nom.length + 1));
                }
            });
        }
        return cookieVal;
    }
});