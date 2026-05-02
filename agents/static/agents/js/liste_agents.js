// ============================================================
// NaissanceChain — JavaScript Liste des Agents (Admin)
// Sélection agent + mise à jour URL + actualisation
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

    // =========================================================
    // SÉLECTION D'UN AGENT : met à jour l'URL sans rechargement
    // puis redirige pour afficher le panneau latéral
    // =========================================================
    window.selectionnerAgent = function (agentId) {
        // Construire l'URL avec le paramètre agent_id
        const urlActuelle = new URL(window.location.href);
        urlActuelle.searchParams.set('agent_id', agentId);
        window.location.href = urlActuelle.toString();
    };


    // =========================================================
    // BOUTON ACTUALISER : recharge la liste sans perdre les filtres
    // =========================================================
    const btnActualiser = document.getElementById('btnActualiser');

    if (btnActualiser) {
        btnActualiser.addEventListener('click', function () {
            // Animation rotation icône
            const icone = btnActualiser.querySelector('i');
            if (icone) {
                icone.style.transition  = 'transform 0.6s ease';
                icone.style.transform   = 'rotate(360deg)';
            }
            setTimeout(function () {
                window.location.reload();
            }, 400);
        });
    }


    // =========================================================
    // MISE EN ÉVIDENCE DE LA LIGNE AGENT SÉLECTIONNÉE
    // =========================================================
    const urlParams   = new URLSearchParams(window.location.search);
    const agentIdUrl  = urlParams.get('agent_id');

    if (agentIdUrl) {
        const ligneActive = document.querySelector(
            `.nc-agent-row[data-agent-id="${agentIdUrl}"]`
        );
        if (ligneActive) {
            ligneActive.classList.add('active');
            // Scroller vers la ligne si nécessaire
            ligneActive.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }


    // =========================================================
    // CONFIRMATION AVANT SUSPENSION
    // =========================================================
    document.querySelectorAll('.nc-btn-suspendre').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const confirmation = confirm(
                'Êtes-vous sûr de vouloir suspendre cet agent ?\n' +
                'Il ne pourra plus accéder au système tant qu\'il est suspendu.'
            );
            if (!confirmation) {
                e.preventDefault();
            }
        });
    });
});