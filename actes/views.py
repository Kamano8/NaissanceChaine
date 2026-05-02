# ============================================================
# NaissanceChain — Vues de l'app Actes
# Saisie multi-étapes + historique + acte généré
# ============================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ActeNaissance, StatutSynchronisation
from agents.models import Agent


# ============================================================
# FORMULAIRE MULTI-ÉTAPES : NOUVEAU ACTE (maquettes p.2)
# Étapes : Enfant → Parents → Lieu → Preuves → Validation
# ============================================================

@login_required
def vue_nouveau_acte(request):
    """
    Formulaire multi-étapes de saisie d'un acte de naissance.
    L'état de l'acte en cours est stocké en session Django.
    """
    agent = getattr(request.user, 'profil_agent', None)
    if not agent:
        messages.error(request, "Accès réservé aux agents de terrain.")
        return redirect('accounts:connexion')

    # Récupère l'étape actuelle (défaut : enfant)
    etapes        = ['enfant', 'parents', 'lieu', 'preuves', 'validation']
    etape_actuelle = request.GET.get('etape', 'enfant')
    if etape_actuelle not in etapes:
        etape_actuelle = 'enfant'

    index_etape   = etapes.index(etape_actuelle)

    if request.method == 'POST':
        # Sauvegarder les données de cette étape en session
        donnees_session = request.session.get('nouvel_acte', {})
        donnees_session[etape_actuelle] = request.POST.dict()
        donnees_session[etape_actuelle].pop('csrfmiddlewaretoken', None)
        request.session['nouvel_acte'] = donnees_session
        request.session.modified       = True

        # Action : sauvegarder brouillon
        if 'sauvegarder_brouillon' in request.POST:
            messages.info(request, "Acte sauvegardé en brouillon local.")
            return redirect(f'/actes/nouveau/?etape={etape_actuelle}')

        # Action : soumettre l'acte complet (étape validation)
        if etape_actuelle == 'validation':
            return _finaliser_acte(request, agent, donnees_session)

        # Action : étape suivante
        etape_suivante = etapes[index_etape + 1]
        return redirect(f'/actes/nouveau/?etape={etape_suivante}')

    # GET : afficher le formulaire de l'étape courante
    donnees_session = request.session.get('nouvel_acte', {})

    contexte = {
        'etape_actuelle': etape_actuelle,
        'index_etape':    index_etape,
        'etapes':         etapes,
        'nb_etapes':      len(etapes),
        'donnees':        donnees_session.get(etape_actuelle, {}),
        'agent':          agent,
        'langue':         request.GET.get('langue', 'Français'),
        'est_hors_ligne': not agent.est_en_ligne,
    }
    return render(request, 'actes/nouveau_acte.html', contexte)


def _finaliser_acte(request, agent, donnees):
    """
    Crée l'ActeNaissance en base depuis les données de session.
    Déclenche ensuite la synchronisation blockchain.
    """
    try:
        d_enfant  = donnees.get('enfant',  {})
        d_parents = donnees.get('parents', {})
        d_lieu    = donnees.get('lieu',    {})

        acte = ActeNaissance.objects.create(
            # Enfant
            nom_enfant       = d_enfant.get('nom_enfant', ''),
            prenom_enfant    = d_enfant.get('prenom_enfant', ''),
            date_naissance   = d_enfant.get('date_naissance') or timezone.now().date(),
            sexe             = d_enfant.get('sexe', 'M'),
            # Parents
            nom_pere         = d_parents.get('nom_pere', ''),
            nin_pere         = d_parents.get('nin_pere', ''),
            pere_present     = 'pere_present' in d_parents,
            nom_mere         = d_parents.get('nom_mere', ''),
            profession_mere  = d_parents.get('profession_mere', ''),
            # Lieu
            lieu_naissance   = d_lieu.get('lieu_naissance', ''),
            region_naissance = d_lieu.get('region', agent.utilisateur.region),
            prefecture       = d_lieu.get('prefecture', agent.utilisateur.prefecture),
            # Agent
            agent            = agent,
            centre_etat_civil = agent.centre_etat_civil,
            # GPS depuis session agent
            latitude_enregistrement  = agent.latitude_actuelle,
            longitude_enregistrement = agent.longitude_actuelle,
            precision_gps            = agent.precision_gps,
            # Statut initial
            mode_hors_ligne = not agent.est_en_ligne,
            statut_sync     = StatutSynchronisation.EN_ATTENTE,
        )

        # Générer le QR Code
        _generer_qr_code(acte)

        # Synchroniser avec la blockchain si en ligne
        if agent.est_en_ligne:
            from .blockchain import synchroniser_acte
            synchroniser_acte(acte)

        # Nettoyer la session
        request.session.pop('nouvel_acte', None)

        messages.success(request, f"Acte {acte.reference} enregistré avec succès !")
        return redirect(f'/actes/{acte.pk}/genere/')

    except Exception as e:
        messages.error(request, f"Erreur lors de l'enregistrement : {str(e)}")
        return redirect('/actes/nouveau/?etape=enfant')


def _generer_qr_code(acte):
    """Génère et sauvegarde le QR Code de l'acte"""
    try:
        import qrcode
        from io import BytesIO
        from django.core.files import File

        donnees_qr = f"NC:{acte.reference}|{acte.get_nom_complet_enfant()}|{acte.date_naissance}"
        img        = qrcode.make(donnees_qr)
        buffer     = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        acte.qr_code.save(f"qr_{acte.reference}.png", File(buffer), save=True)
    except Exception:
        pass  # QR Code optionnel, ne bloque pas l'enregistrement


# ============================================================
# ACTE GÉNÉRÉ (maquette page 3)
# ============================================================

@login_required
def vue_acte_genere(request, acte_id):
    """
    Page de confirmation après génération d'un acte.
    Affiche le certificat avec QR Code et hash blockchain.
    """
    acte = get_object_or_404(ActeNaissance, pk=acte_id)

    # Vérifier que l'agent a accès à cet acte
    agent = getattr(request.user, 'profil_agent', None)
    if agent and acte.agent != agent and not request.user.est_admin_national:
        messages.error(request, "Accès refusé.")
        return redirect('agents:tableau_de_bord')

    contexte = {'acte': acte}
    return render(request, 'actes/acte_genere.html', contexte)


# ============================================================
# HISTORIQUE DES ACTES (maquette page 4)
# ============================================================

@login_required
def vue_historique(request):
    """
    Liste des actes enregistrés par l'agent connecté.
    Avec filtres : Tous / Synchronisés / En attente / Erreurs.
    """
    agent = getattr(request.user, 'profil_agent', None)
    if not agent:
        messages.error(request, "Accès réservé aux agents.")
        return redirect('accounts:connexion')

    actes = ActeNaissance.objects.filter(agent=agent)

    # Filtre par statut
    filtre = request.GET.get('filtre', 'tous')
    if filtre == 'synchronises':
        actes = actes.filter(statut_sync=StatutSynchronisation.SYNCHRONISE)
    elif filtre == 'en_attente':
        actes = actes.filter(statut_sync=StatutSynchronisation.EN_ATTENTE)
    elif filtre == 'erreurs':
        actes = actes.filter(statut_sync=StatutSynchronisation.ERREUR)

    # Recherche par nom enfant
    recherche = request.GET.get('q', '').strip()
    if recherche:
        actes = actes.filter(nom_enfant__icontains=recherche) | \
                actes.filter(prenom_enfant__icontains=recherche)

    contexte = {
        'actes':    actes,
        'filtre':   filtre,
        'recherche': recherche,
        'agent':    agent,
        'nb_total':        ActeNaissance.objects.filter(agent=agent).count(),
        'nb_synchronises': ActeNaissance.objects.filter(agent=agent, statut_sync='synchronise').count(),
        'nb_en_attente':   ActeNaissance.objects.filter(agent=agent, statut_sync='en_attente').count(),
        'nb_erreurs':      ActeNaissance.objects.filter(agent=agent, statut_sync='erreur').count(),
    }
    return render(request, 'actes/historique.html', contexte)


# ============================================================
# DÉTAIL D'UN ACTE
# ============================================================

@login_required
def vue_detail_acte(request, acte_id):
    """Détail complet d'un acte de naissance"""
    acte = get_object_or_404(ActeNaissance, pk=acte_id)
    return render(request, 'actes/detail_acte.html', {'acte': acte})


# ============================================================
# TÉLÉCHARGEMENT PDF
# ============================================================

@login_required
def vue_telecharger_pdf(request, acte_id):
    """Génère et télécharge le PDF officiel de l'acte"""
    from .pdf import generer_pdf_acte
    acte     = get_object_or_404(ActeNaissance, pk=acte_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="acte_{acte.reference}.pdf"'
    generer_pdf_acte(acte, response)
    return response