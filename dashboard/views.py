# ============================================================
# NaissanceChain — Dashboard National (maquette page 5)
# Accessible : Super Admin, Admin National, Admin Préfectoral
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import Utilisateur, RoleChoices
from accounts.forms import FormulaireCreationUtilisateur


def _admin_requis(user):
    return user.est_super_admin or user.est_admin_national or user.est_admin_prefectoral


@login_required
def vue_dashboard(request):
    if not (
        request.user.est_super_admin or
        request.user.est_admin_national or
        request.user.est_admin_prefectoral
    ):
        messages.error(request, "Accès refusé. Espace réservé aux administrateurs.")
        return redirect('accounts:connexion')

    from actes.models import ActeNaissance, StatutSynchronisation
    from agents.models import Agent

    aujourd_hui = timezone.now().date()

    # ── Stats enfants enregistrés ──
    nb_total        = ActeNaissance.objects.count()
    nb_synchronise  = ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.SYNCHRONISE).count()
    nb_en_attente   = ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.EN_ATTENTE).count()
    nb_erreur       = ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.ERREUR).count()
    nb_aujourd_hui  = ActeNaissance.objects.filter(date_creation__date=aujourd_hui).count()
    nb_ce_mois      = ActeNaissance.objects.filter(
        date_creation__year=aujourd_hui.year,
        date_creation__month=aujourd_hui.month
    ).count()

    # ── KPIs réels ──
    nb_actes_total      = nb_total
    nb_non_synchronises = nb_en_attente + nb_erreur
    nb_agents_actifs    = Agent.objects.filter(statut='actif', est_en_ligne=True).count()
    nb_agents_total     = Agent.objects.filter(statut='actif').count()

    # Taux de couverture = % actes synchronisés
    taux_couverture = round(
        ((nb_actes_total - nb_non_synchronises) / nb_actes_total * 100) if nb_actes_total else 0,
        1
    )

    # ── Top 3 agents (par nb d'actes ce mois) ──
    from django.db.models import Count, Q
    from datetime import date
    debut_mois = aujourd_hui.replace(day=1)
    top_agents_qs = (
        Agent.objects.filter(statut='actif')
        .select_related('utilisateur')
        .annotate(nb_actes=Count(
            'actes',
            filter=Q(actes__date_creation__date__gte=debut_mois)
        ))
        .order_by('-nb_actes')[:3]
    )
    top_agents = [
        {
            'nom':      a.get_nom_complet(),
            'zone':     a.secteur,
            'actes':    a.nb_actes,
            'en_ligne': a.est_en_ligne,
        }
        for a in top_agents_qs
    ]

    # ── Régions avec stats réelles ──
    from accounts.models import RegionGuinee
    regions_data = []
    for valeur, label in RegionGuinee.choices:
        nb = ActeNaissance.objects.filter(agent__utilisateur__region=valeur).count()
        if   nb >= 8000: niveau = 'eleve'
        elif nb >= 3000: niveau = 'moyen'
        else:            niveau = 'faible'
        regions_data.append({
            'nom':    label.upper(),
            'actes':  nb,
            'niveau': niveau,
            'focus':  valeur == 'conakry',
        })

    # ── Événements blockchain récents ──
    derniers_actes = ActeNaissance.objects.filter(
        statut_sync='synchronise'
    ).select_related('agent__utilisateur').order_by('-date_creation')[:3]

    evenements_blockchain = []
    for acte in derniers_actes:
        evenements_blockchain.append({
            'temps':       f"Il y a {timezone.now() - acte.date_creation}".split('.')[0],
            'description': f"Acte {acte.reference} synchronisé — Agent {acte.agent.get_nom_complet()}",
        })

    # ── Zones à risque réelles ──
    zones_risque = []
    for valeur, label in RegionGuinee.choices:
        total_region = ActeNaissance.objects.filter(agent__utilisateur__region=valeur).count()
        sync_region  = ActeNaissance.objects.filter(
            agent__utilisateur__region=valeur,
            statut_sync='synchronise'
        ).count()
        if total_region > 0:
            taux = round(sync_region / total_region * 100)
            if taux < 90:
                couleur = 'rouge' if taux < 70 else 'orange'
                zones_risque.append({'nom': label, 'taux': taux, 'couleur': couleur})
    zones_risque = sorted(zones_risque, key=lambda x: x['taux'])[:3]

    contexte = {
        'taux_couverture':       taux_couverture,
        'nb_actes_total':        nb_actes_total,
        'nb_non_synchronises':   nb_non_synchronises,
        'nb_agents_actifs':      nb_agents_actifs,
        'nb_agents_total':       nb_agents_total,
        'alerte_critique':       nb_non_synchronises > 50,
        'regions':               regions_data,
        'evenements_blockchain': evenements_blockchain,
        'top_agents':            top_agents,
        'zones_risque':          zones_risque,
        # Stats enfants
        'nb_total':       nb_total,
        'nb_synchronise': nb_synchronise,
        'nb_en_attente':  nb_en_attente,
        'nb_erreur':      nb_erreur,
        'nb_aujourd_hui': nb_aujourd_hui,
        'nb_ce_mois':     nb_ce_mois,
    }
    return render(request, 'dashboard/dashboard.html', contexte)


@login_required
def vue_utilisateurs(request):
    """Gestion des utilisateurs : Agents, Admins, Familles"""
    if not _admin_requis(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    filtre = request.GET.get('role', 'tous')
    q      = request.GET.get('q', '').strip()

    utilisateurs = Utilisateur.objects.all().order_by('-date_joined')

    if filtre == 'agents':
        utilisateurs = utilisateurs.filter(role=RoleChoices.AGENT)
    elif filtre == 'admins':
        utilisateurs = utilisateurs.filter(role__in=[
            RoleChoices.SUPER_ADMIN, RoleChoices.ADMIN_NATIONAL, RoleChoices.ADMIN_PREFECTORAL
        ])
    elif filtre == 'familles':
        utilisateurs = utilisateurs.filter(role=RoleChoices.CITOYEN)

    if q:
        utilisateurs = utilisateurs.filter(
            nom__icontains=q
        ) | Utilisateur.objects.filter(prenom__icontains=q) | Utilisateur.objects.filter(email__icontains=q)
        if filtre != 'tous':
            if filtre == 'agents':
                utilisateurs = utilisateurs.filter(role=RoleChoices.AGENT)
            elif filtre == 'admins':
                utilisateurs = utilisateurs.filter(role__in=[
                    RoleChoices.SUPER_ADMIN, RoleChoices.ADMIN_NATIONAL, RoleChoices.ADMIN_PREFECTORAL
                ])
            elif filtre == 'familles':
                utilisateurs = utilisateurs.filter(role=RoleChoices.CITOYEN)

    contexte = {
        'utilisateurs':  utilisateurs,
        'filtre':        filtre,
        'q':             q,
        'nb_total':      Utilisateur.objects.count(),
        'nb_agents':     Utilisateur.objects.filter(role=RoleChoices.AGENT).count(),
        'nb_admins':     Utilisateur.objects.filter(role__in=[
                             RoleChoices.SUPER_ADMIN, RoleChoices.ADMIN_NATIONAL, RoleChoices.ADMIN_PREFECTORAL
                         ]).count(),
        'nb_familles':   Utilisateur.objects.filter(role=RoleChoices.CITOYEN).count(),
        'nb_actifs':     Utilisateur.objects.filter(is_active=True).count(),
        'nb_inactifs':   Utilisateur.objects.filter(is_active=False).count(),
        'filtres': [
            ('tous',     'Tous',             'fa-solid fa-users'),
            ('agents',   'Agents',           'fa-solid fa-id-badge'),
            ('admins',   'Administrateurs',  'fa-solid fa-user-shield'),
            ('familles', 'Familles',         'fa-solid fa-house-user'),
        ],
    }
    return render(request, 'dashboard/utilisateurs.html', contexte)


@login_required
def vue_creer_utilisateur(request):
    """Création d'un utilisateur par l'admin"""
    if not _admin_requis(request.user):
        return redirect('dashboard:index')

    if request.method == 'POST':
        formulaire = FormulaireCreationUtilisateur(request.POST, request.FILES)
        if formulaire.is_valid():
            utilisateur = formulaire.save()
            messages.success(request, f"Utilisateur {utilisateur.get_nom_complet()} créé avec succès.")
            return redirect('dashboard:utilisateurs')
        messages.error(request, "Veuillez corriger les erreurs.")
    else:
        formulaire = FormulaireCreationUtilisateur()

    return render(request, 'dashboard/creer_utilisateur.html', {'formulaire': formulaire})


@login_required
def vue_toggle_utilisateur(request, pk):
    """Activer / Désactiver un compte utilisateur"""
    if not _admin_requis(request.user):
        return redirect('dashboard:index')
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if utilisateur == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
    else:
        utilisateur.is_active = not utilisateur.is_active
        utilisateur.save(update_fields=['is_active'])
        etat = "activé" if utilisateur.is_active else "désactivé"
        messages.success(request, f"Compte de {utilisateur.get_nom_complet()} {etat}.")
    return redirect('dashboard:utilisateurs')


@login_required
def vue_supprimer_utilisateur(request, pk):
    """Supprimer un utilisateur"""
    if not request.user.est_super_admin:
        messages.error(request, "Seul le Super Admin peut supprimer un compte.")
        return redirect('dashboard:utilisateurs')
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if utilisateur == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
    else:
        nom = utilisateur.get_nom_complet()
        utilisateur.delete()
        messages.success(request, f"Compte de {nom} supprimé.")
    return redirect('dashboard:utilisateurs')