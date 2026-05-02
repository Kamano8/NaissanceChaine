# ============================================================
# NaissanceChain — Vues de l'app Agents
# Tableau de bord agent terrain + gestion admin des agents
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Agent, AlerteZone, EvenementActivite
from .forms import FormulairePositionGPS, FormulaireCreationAgent


# ============================================================
# TABLEAU DE BORD AGENT DE TERRAIN (vue mobile — maquette p.1)
# ============================================================

@login_required
def tableau_de_bord_agent(request):
    agent = getattr(request.user, 'profil_agent', None)
    if not agent:
        # Rediriger vers l'index du dashboard plutôt que la connexion 
        # pour éviter une boucle infinie si l'utilisateur est déjà connecté.
        messages.error(request, "Accès refusé : votre compte n'est pas configuré comme un profil agent.")
        return redirect('dashboard:index')

    agent.est_en_ligne      = True
    agent.derniere_activite = timezone.now()
    agent.save(update_fields=['est_en_ligne', 'derniere_activite'])

    flux_activite   = EvenementActivite.objects.filter(agent=agent).select_related('agent')[:10]

    contexte = {
        'agent':             agent,
        'flux_activite':     flux_activite,
        'actes_aujourd_hui': agent.actes_aujourd_hui,
        'actes_non_sync':    agent.actes_non_synchronises,
    }
    return render(request, 'agents/tableau_de_bord.html', contexte)


@login_required
@require_POST
def mettre_a_jour_gps(request):
    import json
    agent = getattr(request.user, 'profil_agent', None)
    if not agent:
        return JsonResponse({'succes': False, 'erreur': 'Profil agent introuvable'}, status=404)
    try:
        donnees = json.loads(request.body)
        agent.latitude_actuelle  = donnees.get('latitude')
        agent.longitude_actuelle = donnees.get('longitude')
        agent.precision_gps      = donnees.get('precision')
        agent.gps_mis_a_jour_le  = timezone.now()
        agent.save(update_fields=['latitude_actuelle','longitude_actuelle','precision_gps','gps_mis_a_jour_le'])
        return JsonResponse({'succes': True})
    except (json.JSONDecodeError, KeyError) as e:
        return JsonResponse({'succes': False, 'erreur': str(e)}, status=400)


@login_required
@require_POST
def marquer_flux_lu(request):
    agent = getattr(request.user, 'profil_agent', None)
    if not agent:
        return JsonResponse({'succes': False}, status=404)
    EvenementActivite.objects.filter(agent=agent, est_lu=False).update(est_lu=True)
    return JsonResponse({'succes': True})


@login_required
def liste_agents(request):
    if not (request.user.est_admin_national or request.user.est_super_admin):
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    agents_qs     = Agent.objects.select_related('utilisateur').all()
    recherche     = request.GET.get('q', '').strip()
    filtre_statut = request.GET.get('statut', '')

    if recherche:
        agents_qs = agents_qs.filter(utilisateur__nom__icontains=recherche) | \
                    agents_qs.filter(utilisateur__prenom__icontains=recherche) | \
                    agents_qs.filter(code_agent__icontains=recherche)
    if filtre_statut:
        agents_qs = agents_qs.filter(statut=filtre_statut)

    agent_selectionne_id = request.GET.get('agent_id')
    agent_selectionne    = None
    if agent_selectionne_id:
        agent_selectionne = get_object_or_404(Agent.objects.select_related('utilisateur'), pk=agent_selectionne_id)

    paginator   = Paginator(agents_qs, 20)
    page_obj    = paginator.get_page(request.GET.get('page'))

    contexte = {
        'page_obj':          page_obj,
        'nb_agents':         agents_qs.count(),
        'recherche':         recherche,
        'filtre_statut':     filtre_statut,
        'agent_selectionne': agent_selectionne,
    }
    return render(request, 'agents/liste_agents.html', contexte)


@login_required
@require_POST
def changer_statut_agent(request, agent_id):
    if not (request.user.est_admin_national or request.user.est_super_admin):
        return JsonResponse({'succes': False, 'erreur': 'Accès refusé'}, status=403)
    agent  = get_object_or_404(Agent, pk=agent_id)
    action = request.POST.get('action')
    if action == 'suspendre':
        agent.statut = 'suspendu'; agent.est_en_ligne = False
        agent.save(update_fields=['statut', 'est_en_ligne'])
        messages.warning(request, f"L'agent {agent.code_agent} a été suspendu.")
    elif action == 'reactiver':
        agent.statut = 'actif'
        agent.save(update_fields=['statut'])
        messages.success(request, f"L'agent {agent.code_agent} a été réactivé.")
    return redirect('agents:liste')


@login_required
@require_POST
def creer_agent(request):
    if not (request.user.est_admin_national or request.user.est_super_admin):
        messages.error(request, "Accès refusé.")
        return redirect('agents:liste')

    from accounts.models import Utilisateur, RoleChoices

    email      = request.POST.get('email', '').strip()
    nom        = request.POST.get('nom', '').strip()
    prenom     = request.POST.get('prenom', '').strip()
    telephone  = request.POST.get('telephone', '').strip()
    region     = request.POST.get('region', '').strip()
    password   = request.POST.get('password', '')
    code_agent = request.POST.get('code_agent', '').strip()
    secteur    = request.POST.get('secteur', '').strip()
    centre     = request.POST.get('centre_etat_civil', '').strip()

    if Utilisateur.objects.filter(email=email).exists():
        messages.error(request, f"Un compte avec l'email {email} existe déjà.")
        return redirect('agents:liste')
    if Agent.objects.filter(code_agent=code_agent).exists():
        messages.error(request, f"Le code agent {code_agent} est déjà utilisé.")
        return redirect('agents:liste')

    utilisateur = Utilisateur.objects.create_user(
        email=email, password=password,
        nom=nom, prenom=prenom,
        telephone=telephone, region=region,
        role=RoleChoices.AGENT,
    )
    Agent.objects.create(
        utilisateur=utilisateur,
        code_agent=code_agent,
        secteur=secteur,
        centre_etat_civil=centre,
    )
    messages.success(request, f"Agent {prenom} {nom} ({code_agent}) créé avec succès.")
    return redirect('agents:liste')


@login_required
@require_POST
def reassigner_agent(request, agent_id):
    if not (request.user.est_admin_national or request.user.est_super_admin):
        messages.error(request, "Accès refusé.")
        return redirect('agents:liste')

    agent   = get_object_or_404(Agent, pk=agent_id)
    secteur = request.POST.get('secteur', '').strip()
    region  = request.POST.get('region', '').strip()

    if secteur:
        agent.secteur = secteur
        agent.save(update_fields=['secteur'])
    if region:
        agent.utilisateur.region = region
        agent.utilisateur.save(update_fields=['region'])

    messages.success(request, f"Agent {agent.code_agent} réassigné à {secteur}.")
    return redirect('agents:liste')



def vue_securite(request):
    return render(request, 'agents/securite.html')


@login_required
def vue_profil(request):
    """Gère l'affichage et la mise à jour de la photo de l'agent."""
    agent = getattr(request.user, 'profil_agent', None)

    if not agent:
        messages.error(request, "Accès refusé : profil agent introuvable.")
        return redirect('dashboard:index')

    if request.method == 'POST' and request.FILES.get('photo'):
        # La photo est portée par le compte Utilisateur, pas par le profil Agent
        agent.utilisateur.photo = request.FILES['photo']
        agent.utilisateur.save(update_fields=['photo'])
        messages.success(request, "Votre photo de profil a été mise à jour.")
        return redirect('agents:profil')

    return render(request, 'agents/profil.html', {
        'agent': agent,
    })

@login_required
def telecharger_extrait(request, reference):
    """Génère une vue imprimable de l'extrait de naissance."""
    from actes.models import ActeNaissance
    acte = get_object_or_404(ActeNaissance, reference=reference)
    return render(request, 'actes/extrait_naissance_pdf.html', {
        'acte': acte,
        'date_impression': timezone.now(),
    })