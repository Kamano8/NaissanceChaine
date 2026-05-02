// ============================================================
// NaissanceChain — JavaScript global (sidebar, notifications)
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

    // --- Toggle sidebar (responsive) ---
    const boutonToggle = document.getElementById('sidebarToggle');
    const sidebar      = document.getElementById('sidebar');

    if (boutonToggle && sidebar) {
        boutonToggle.addEventListener('click', function () {
            sidebar.classList.toggle('ouvert');
        });

        // Fermer la sidebar en cliquant en dehors
        document.addEventListener('click', function (e) {
            if (window.innerWidth <= 992) {
                if (!sidebar.contains(e.target) && !boutonToggle.contains(e.target)) {
                    sidebar.classList.remove('ouvert');
                }
            }
        });
    }

    // --- Fermeture automatique des alertes après 5 secondes ---
    const alertes = document.querySelectorAll('.nc-alert');
    alertes.forEach(function (alerte) {
        setTimeout(function () {
            const fermer = new bootstrap.Alert(alerte);
            fermer.close();
        }, 5000);
    });
});