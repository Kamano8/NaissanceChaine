# ============================================================
# NaissanceChain — Vues d'authentification
# ============================================================

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import View

from .forms import FormulaireConnexion, FormulaireModificationProfil, FormulaireInscriptionCitoyen
from .models import RoleChoices


class VueConnexion(View):
    """
    Vue de connexion principale.
    Redirige chaque rôle vers son tableau de bord approprié.
    """
    template_name = 'accounts/connexion.html'

    def get(self, request):
        # Si déjà connecté, rediriger directement
        if request.user.is_authenticated:
            return self.rediriger_selon_role(request.user)
        formulaire = FormulaireConnexion(request)
        return render(request, self.template_name, {'formulaire': formulaire})

    def post(self, request):
        formulaire = FormulaireConnexion(request, data=request.POST)
        if formulaire.is_valid():
            utilisateur = formulaire.get_user()
            login(request, utilisateur)

            # Enregistrer l'IP de connexion pour l'audit
            utilisateur.derniere_connexion_ip = self._get_ip_client(request)
            utilisateur.save(update_fields=['derniere_connexion_ip'])

            messages.success(
                request,
                f"Bienvenue, {utilisateur.get_nom_complet()} !"
            )
            return self.rediriger_selon_role(utilisateur)

        messages.error(request, "Email ou mot de passe incorrect.")
        return render(request, self.template_name, {'formulaire': formulaire})

    @staticmethod
    def rediriger_selon_role(utilisateur):
        """Redirige vers le bon tableau de bord selon le rôle"""
        redirections = {
            RoleChoices.SUPER_ADMIN:       reverse('dashboard:index'),
            RoleChoices.ADMIN_NATIONAL:    reverse('dashboard:index'),
            RoleChoices.ADMIN_PREFECTORAL: reverse('dashboard:index'),
            RoleChoices.AGENT:             reverse('agents:tableau_de_bord'),
            RoleChoices.CITOYEN:           reverse('verification:index'),
        }
        url = redirections.get(utilisateur.role, reverse('dashboard:index'))
        return redirect(url)

    def _get_ip_client(self, request):
        """Récupère l'IP réelle du client (derrière proxy)"""
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class VueInscription(View):
    """
    Auto-inscription réservée aux citoyens (familles).
    Le rôle CITOYEN est assigné automatiquement.
    """
    template_name = 'accounts/inscription.html'

    def get(self, request):
        if request.user.is_authenticated:
            return VueConnexion.rediriger_selon_role(request.user)
        return render(request, self.template_name, {'formulaire': FormulaireInscriptionCitoyen()})

    def post(self, request):
        formulaire = FormulaireInscriptionCitoyen(request.POST)
        if formulaire.is_valid():
            utilisateur = formulaire.save()
            login(request, utilisateur)
            messages.success(request, f"Bienvenue, {utilisateur.get_nom_complet()} ! Votre compte citoyen a été créé.")
            return redirect('verification:index')
        return render(request, self.template_name, {'formulaire': formulaire})


class VueDeconnexion(View):
    """Déconnexion et redirection vers la page de connexion"""

    def get(self, request):
        logout(request)
        messages.info(request, "Vous avez été déconnecté avec succès.")
        return redirect('accounts:connexion')


@login_required
def vue_profil(request):
    """Page de profil de l'utilisateur connecté avec modification"""
    if request.method == 'POST':
        formulaire = FormulaireModificationProfil(request.POST, request.FILES, instance=request.user)
        if formulaire.is_valid():
            formulaire.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('accounts:profil')
        messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        formulaire = FormulaireModificationProfil(instance=request.user)

    return render(request, 'accounts/profil.html', {
        'utilisateur': request.user,
        'formulaire':  formulaire,
    })


@login_required
def vue_redirection_role(request):
    """
    Vue intermédiaire pour rediriger l'utilisateur vers son tableau de bord
    selon son rôle après une action (ex: connexion, réinitialisation).
    """
    return VueConnexion.rediriger_selon_role(request.user)


# --- Vues pour la réinitialisation du mot de passe ---

class VueMotDePasseOublie(auth_views.PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

class VueMotDePasseOublieEnvoye(auth_views.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class VueMotDePasseReinitialiser(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class VueMotDePasseReinitialiseTermine(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'