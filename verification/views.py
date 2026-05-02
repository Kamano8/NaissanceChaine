# ============================================================
# NaissanceChain — Vues Vérification (maquettes p.6, 9, 10)
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DemandeActe, StatutDemande


def vue_portail_public(request):
    """Portail public citoyen de vérification — maquette page 9"""
    return render(request, 'verification/portail_public.html')


def vue_suivi_demande(request):
    """Suivi de demande citoyen — maquette page 10"""
    reference = request.GET.get('ref', '').strip()
    acte      = None
    erreur    = None

    if reference:
        try:
            from actes.models import ActeNaissance
            acte = ActeNaissance.objects.get(reference=reference)
        except ActeNaissance.DoesNotExist:
            erreur = f"Aucun acte trouvé pour la référence : {reference}"

    return render(request, 'verification/suivi_demande.html', {
        'reference': reference, 'acte': acte, 'erreur': erreur
    })


@login_required
def vue_outil_verification(request):
    """Outil de vérification admin — maquette page 6"""
    from accounts.models import RoleChoices
    if not (request.user.est_admin_national or request.user.est_super_admin
            or request.user.est_admin_prefectoral or request.user.role == RoleChoices.AGENT):
        return redirect('verification:public')

    from actes.models import ActeNaissance
    reference = request.GET.get('ref', '').strip()
    resultat  = None

    if reference:
        try:
            acte     = ActeNaissance.objects.select_related('agent__utilisateur').get(reference=reference)
            resultat = {'acte': acte, 'valide': acte.est_synchronise}
        except ActeNaissance.DoesNotExist:
            resultat = {'acte': None, 'valide': False, 'erreur': f'Aucun acte trouvé pour la référence : {reference}'}

    derniers_actes = ActeNaissance.objects.select_related('agent__utilisateur').order_by('-date_creation')[:10]

    return render(request, 'verification/outil_verification.html', {
        'reference':     reference,
        'resultat':      resultat,
        'derniers_actes': derniers_actes,
    })


@login_required
def vue_mes_demandes(request):
    """Liste des demandes du citoyen connecté"""
    if not request.user.est_citoyen:
        return redirect('verification:outil')
    demandes = DemandeActe.objects.filter(citoyen=request.user)
    return render(request, 'verification/mes_demandes.html', {'demandes': demandes})


@login_required
def vue_nouvelle_demande(request):
    """Formulaire de soumission d'une nouvelle demande d'acte"""
    if not request.user.est_citoyen:
        return redirect('verification:outil')

    if request.method == 'POST':
        d = request.POST
        DemandeActe.objects.create(
            citoyen        = request.user,
            nom_enfant     = d.get('nom_enfant', '').strip(),
            prenom_enfant  = d.get('prenom_enfant', '').strip(),
            date_naissance = d.get('date_naissance'),
            lieu_naissance = d.get('lieu_naissance', '').strip(),
            reference_acte = d.get('reference_acte', '').strip(),
            motif          = d.get('motif', '').strip(),
        )
        messages.success(request, "Votre demande a été soumise avec succès. L'administration va la traiter.")
        return redirect('verification:mes_demandes')

    return render(request, 'verification/nouvelle_demande.html')


@login_required
def vue_scanner_acte(request):
    """Résultat après scan QR ou saisie manuelle de référence par le citoyen"""
    if not request.user.est_citoyen:
        return redirect('verification:outil')

    reference = request.GET.get('ref', '').strip()
    acte      = None
    erreur    = None

    if reference:
        try:
            from actes.models import ActeNaissance
            acte = ActeNaissance.objects.get(reference=reference)
        except ActeNaissance.DoesNotExist:
            erreur = f"Aucun acte trouvé pour la référence : {reference}"

    return render(request, 'verification/scanner_acte.html', {
        'reference': reference,
        'acte':      acte,
        'erreur':    erreur,
    })


@login_required
def vue_index(request):
    if request.user.est_citoyen:
        return redirect('verification:mes_demandes')
    return vue_outil_verification(request)