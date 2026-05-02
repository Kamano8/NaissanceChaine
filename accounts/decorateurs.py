# ============================================================
# accounts/decorateurs.py
# Décorateurs personnalisés de contrôle d'accès par rôle
# Utilisés dans toutes les vues NaissanceChain
# ============================================================

from functools import wraps
from django.shortcuts import redirect
from django.contrib   import messages
from .models          import RoleChoices


def _verifier_role(roles_autorises):
    """
    Fabrique de décorateur générique.
    Vérifie si l'utilisateur connecté possède l'un des rôles autorisés.
    """
    def decorateur(fonction_vue):
        @wraps(fonction_vue)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Vous devez être connecté pour accéder à cette page.")
                return redirect('accounts:connexion')

            if str(request.user.role) not in [str(r) for r in roles_autorises]:
                messages.error(
                    request,
                    "Accès refusé. Vous n'avez pas les droits nécessaires."
                )
                return redirect('accounts:redirection_role')

            return fonction_vue(request, *args, **kwargs)
        return wrapper
    return decorateur


# ---- Accès Super Administrateur uniquement ----
def super_admin_requis(fonction_vue):
    """Réserve la vue aux Super Administrateurs."""
    return _verifier_role([RoleChoices.SUPER_ADMIN])(fonction_vue)


# ---- Accès tous les administrateurs ----
def admin_requis(fonction_vue):
    """Réserve la vue aux administrateurs (tous niveaux)."""
    return _verifier_role([
        RoleChoices.SUPER_ADMIN,
        RoleChoices.ADMIN_NATIONAL,
        RoleChoices.ADMIN_PREFECTORAL,
    ])(fonction_vue)


# ---- Accès agents de terrain ----
def agent_requis(fonction_vue):
    """Réserve la vue aux agents de terrain."""
    return _verifier_role([
        RoleChoices.AGENT,
        RoleChoices.SUPER_ADMIN,   # Super admin peut tout voir
    ])(fonction_vue)


# ---- Accès admin ou agent ----
def agent_ou_admin_requis(fonction_vue):
    """Autorise agents et administrateurs."""
    return _verifier_role([
        RoleChoices.SUPER_ADMIN,
        RoleChoices.ADMIN_NATIONAL,
        RoleChoices.ADMIN_PREFECTORAL,
        RoleChoices.AGENT,
    ])(fonction_vue)