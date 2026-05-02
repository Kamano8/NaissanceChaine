# ============================================================
# audit/middleware.py
# Middleware NaissanceChain — Journal d'audit automatique
# Enregistre toutes les requêtes importantes pour la sécurité
# ============================================================

import json
from django.utils import timezone


class AuditMiddleware:
    """
    Middleware qui journalise automatiquement certaines actions
    sensibles effectuées sur la plateforme (POST, DELETE, etc.)
    """

    # Actions à journaliser (méthodes HTTP)
    METHODES_A_JOURNALISER = {'POST', 'PUT', 'PATCH', 'DELETE'}

    # Chemins à exclure du journal (fichiers statiques, admin interne, etc.)
    CHEMINS_EXCLUS = [
        '/static/',
        '/media/',
        '/favicon.ico',
        '/admin/jsi18n/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Traiter la requête normalement
        reponse = self.get_response(request)

        # Journaliser uniquement si nécessaire
        if self._doit_journaliser(request):
            self._enregistrer_action(request, reponse)

        return reponse

    def _doit_journaliser(self, request):
        """Détermine si cette requête doit être journalisée."""
        # Vérifier la méthode HTTP
        if request.method not in self.METHODES_A_JOURNALISER:
            return False

        # Exclure les chemins non pertinents
        for chemin in self.CHEMINS_EXCLUS:
            if request.path.startswith(chemin):
                return False

        # Ne journaliser que les utilisateurs authentifiés
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False

        return True

    def _enregistrer_action(self, request, reponse):
        """
        Enregistre l'action dans le journal d'audit.
        Import tardif pour éviter les erreurs de démarrage.
        """
        try:
            from audit.models import JournalAudit

            adresse_ip = (
                request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                or request.META.get('REMOTE_ADDR', '127.0.0.1')
            )

            JournalAudit.objects.create(
                utilisateur  = request.user,
                action       = f"{request.method} {request.path}",
                chemin       = request.path,
                methode      = request.method,
                adresse_ip   = adresse_ip,
                statut_http  = reponse.status_code,
                region       = request.user.region,
                horodatage   = timezone.now(),
            )
        except Exception:
            # Ne jamais planter à cause du journal d'audit
            pass