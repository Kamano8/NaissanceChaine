/* ============================================================
   static/js/base.js
   JavaScript global NaissanceChain
   Gère : sidebar, notifications, statut réseau, toasts
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

    // =====================================================
    // 1. GESTION DE LA SIDEBAR (ouverture/fermeture)
    // =====================================================
    const sidebar       = document.getElementById('nc-sidebar');
    const btnToggle     = document.getElementById('btn-toggle-sidebar');
    const overlay       = document.getElementById('nc-overlay');

    if (btnToggle && sidebar) {
        btnToggle.addEventListener('click', function () {
            sidebar.classList.toggle('ouverte');
            if (overlay) overlay.classList.toggle('actif');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function () {
            if (sidebar) sidebar.classList.remove('ouverte');
            overlay.classList.remove('actif');
        });
    }

    // Marquer le lien actif dans la sidebar selon l'URL courante
    const cheminCourant = window.location.pathname;
    const liensNav = document.querySelectorAll('.sidebar-lien');
    liensNav.forEach(function (lien) {
        if (lien.getAttribute('href') && cheminCourant.startsWith(lien.getAttribute('href'))) {
            lien.classList.add('actif');
        }
    });

    // =====================================================
    // 2. STATUT RÉSEAU (En ligne / Hors ligne)
    // =====================================================
    const indicateurStatut = document.getElementById('statut-connexion');

    function mettreAJourStatut() {
        if (!indicateurStatut) return;
        const enLigne = navigator.onLine;
        indicateurStatut.className = 'statut-connexion ' + (enLigne ? 'en-ligne' : 'hors-ligne');
        indicateurStatut.innerHTML = `
            <span class="statut-point"></span>
            ${enLigne ? 'En ligne' : 'Hors ligne'}
        `;
    }

    window.addEventListener('online',  mettreAJourStatut);
    window.addEventListener('offline', mettreAJourStatut);
    mettreAJourStatut();

    // =====================================================
    // 3. TOASTS (notifications visuelles)
    // =====================================================
    // Afficher automatiquement les messages Django comme des toasts
    const conteneurMessages = document.getElementById('nc-messages');
    if (conteneurMessages) {
        const toasts = conteneurMessages.querySelectorAll('.nc-toast');
        toasts.forEach(function (toast, index) {
            // Disparition automatique après 4 secondes (décalé selon l'index)
            setTimeout(function () {
                fermerToast(toast);
            }, 4000 + (index * 500));
        });
    }

    // Fermeture manuelle des toasts
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('nc-toast-fermer')) {
            fermerToast(e.target.closest('.nc-toast'));
        }
    });

    function fermerToast(toast) {
        if (!toast) return;
        toast.style.opacity   = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'opacity 0.3s, transform 0.3s';
        setTimeout(() => toast.remove(), 300);
    }

    // =====================================================
    // 4. CONFIRMATION DE SUPPRESSION / ACTIONS CRITIQUES
    // =====================================================
    document.addEventListener('click', function (e) {
        const bouton = e.target.closest('[data-confirmer]');
        if (bouton) {
            const message = bouton.dataset.confirmer || "Êtes-vous sûr de vouloir effectuer cette action ?";
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        }
    });

    // =====================================================
    // 5. RECHERCHE DANS LES TABLEAUX (côté client)
    // =====================================================
    const champRecherche = document.getElementById('recherche-tableau');
    const tableau        = document.getElementById('tableau-principal');

    if (champRecherche && tableau) {
        champRecherche.addEventListener('input', function () {
            const terme = this.value.toLowerCase().trim();
            const lignes = tableau.querySelectorAll('tbody tr');

            lignes.forEach(function (ligne) {
                const texte = ligne.textContent.toLowerCase();
                ligne.style.display = texte.includes(terme) ? '' : 'none';
            });
        });
    }

    // =====================================================
    // 6. FORMATAGE DU TEMPS RELATIF
    // =====================================================
    // Convertit les timestamps en "Il y a 5 min", "Hier", etc.
    const elementsTemps = document.querySelectorAll('[data-horodatage]');
    elementsTemps.forEach(function (el) {
        const timestamp = el.dataset.horodatage;
        if (timestamp) {
            el.textContent = formaterTempsRelatif(new Date(timestamp));
        }
    });

    function formaterTempsRelatif(date) {
        const maintenant = new Date();
        const diffMs     = maintenant - date;
        const diffMin    = Math.floor(diffMs / 60000);
        const diffH      = Math.floor(diffMs / 3600000);
        const diffJ      = Math.floor(diffMs / 86400000);

        if (diffMin < 1)  return "À l'instant";
        if (diffMin < 60) return `Il y a ${diffMin} min`;
        if (diffH   < 24) return `Il y a ${diffH} h`;
        if (diffJ   === 1) return "Hier";
        if (diffJ   < 7)  return `Il y a ${diffJ} jours`;
        return date.toLocaleDateString('fr-FR');
    }

    // =====================================================
    // 7. MISE EN SURBRILLANCE DES HASHS BLOCKCHAIN
    // =====================================================
    // Tronquer les longs hashs pour l'affichage
    const hashs = document.querySelectorAll('.hash-blockchain');
    hashs.forEach(function (el) {
        const complet = el.textContent.trim();
        if (complet.length > 20) {
            el.setAttribute('title', complet);  // Tooltip avec la valeur complète
            el.textContent = complet.substring(0, 10) + '...' + complet.slice(-6);
        }
    });

    // =====================================================
    // 8. COPIER DANS LE PRESSE-PAPIER
    // =====================================================
    document.addEventListener('click', function (e) {
        const bouton = e.target.closest('[data-copier]');
        if (bouton) {
            const cible = bouton.dataset.copier;
            const texte = document.getElementById(cible)?.textContent
                       || document.getElementById(cible)?.value
                       || cible;

            navigator.clipboard.writeText(texte.trim()).then(function () {
                const icone = bouton.querySelector('i');
                if (icone) {
                    const classeOriginale = icone.className;
                    icone.className = 'fas fa-check';
                    setTimeout(() => icone.className = classeOriginale, 1500);
                }
                afficherToast('Copié dans le presse-papier !', 'success');
            });
        }
    });

    // =====================================================
    // Fonction utilitaire : Afficher un toast dynamiquement
    // =====================================================
    window.afficherToast = function (message, type = 'info') {
        const icones = {
            success: 'fa-check-circle',
            error:   'fa-times-circle',
            info:    'fa-info-circle',
            warning: 'fa-exclamation-triangle',
        };

        const toast = document.createElement('div');
        toast.className = `nc-toast ${type}`;
        toast.innerHTML = `
            <i class="fas ${icones[type] || icones.info}"></i>
            <span>${message}</span>
            <button class="nc-toast-fermer"><i class="fas fa-times"></i></button>
        `;

        let conteneur = document.getElementById('nc-messages');
        if (!conteneur) {
            conteneur = document.createElement('div');
            conteneur.id        = 'nc-messages';
            conteneur.className = 'nc-messages';
            document.body.appendChild(conteneur);
        }

        conteneur.appendChild(toast);

        // Disparition automatique
        setTimeout(() => {
            toast.style.opacity    = '0';
            toast.style.transform  = 'translateX(100%)';
            toast.style.transition = 'opacity 0.3s, transform 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };

});