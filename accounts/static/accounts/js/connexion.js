// ============================================================
// NaissanceChain — JavaScript Page de Connexion
// Équipe NEXACORE
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

    // =========================================================
    // 1. AFFICHER / MASQUER LE MOT DE PASSE
    // =========================================================
    const boutonToggle  = document.getElementById('togglePassword');
    const champPassword = document.getElementById('id_password');
    const icone         = document.getElementById('iconeMotDePasse');

    if (boutonToggle && champPassword) {
        boutonToggle.addEventListener('click', function () {
            const estVisible    = champPassword.type === 'text';
            champPassword.type  = estVisible ? 'password' : 'text';
            icone.className     = estVisible
                ? 'fa-solid fa-eye'
                : 'fa-solid fa-eye-slash';
        });
    }

    // =========================================================
    // 2. INDICATEUR DE CHARGEMENT AU SUBMIT
    // =========================================================
    const formulaire   = document.querySelector('.nc-form-connexion');
    const btnConnexion = document.getElementById('btnConnexion');

    if (formulaire && btnConnexion) {
        formulaire.addEventListener('submit', function () {
            const texte   = btnConnexion.querySelector('.nc-btn-texte');
            const loading = btnConnexion.querySelector('.nc-btn-loading');
            if (texte && loading) {
                texte.style.display   = 'none';
                loading.style.display = 'inline-flex';
            }
            btnConnexion.disabled = true;
        });
    }

    // =========================================================
    // 3. FOCUS AUTOMATIQUE SUR L'EMAIL
    // =========================================================
    const champEmail = document.getElementById('id_username');
    if (champEmail && !champEmail.value) {
        setTimeout(function () { champEmail.focus(); }, 400);
    }

    // =========================================================
    // 4. VALIDATION VISUELLE EN TEMPS RÉEL
    // =========================================================
    if (champEmail) {
        champEmail.addEventListener('blur', function () {
            const valide = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value);
            this.style.borderColor = this.value
                ? (valide ? '#0d9e6e' : '#e53e3e')
                : '#e2e8f0';
        });

        champEmail.addEventListener('focus', function () {
            this.style.borderColor = '#1a73e8';
        });
    }
});