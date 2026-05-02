from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone


@login_required
def vue_audit(request):
    if not (request.user.est_admin_national or request.user.est_super_admin):
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    from actes.models import ActeNaissance, StatutSynchronisation
    from .models import JournalAudit

    total_actes      = ActeNaissance.objects.count()
    actes_sync       = ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.SYNCHRONISE).count()
    actes_en_attente = ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.EN_ATTENTE).count()
    actes_erreur     = ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.ERREUR).count()
    derniers_actes   = ActeNaissance.objects.select_related('agent__utilisateur').order_by('-date_creation')[:10]

    journal   = JournalAudit.objects.select_related('utilisateur').order_by('-horodatage')[:20]
    filtre_q  = request.GET.get('q', '').strip()
    if filtre_q:
        journal = JournalAudit.objects.select_related('utilisateur').filter(
            action__icontains=filtre_q
        ).order_by('-horodatage')[:20]
    nb_journal = JournalAudit.objects.count()

    blocs_recents = [
        {'numero': 482091, 'hash': '0000...8f3e', 'txs': 14, 'temps': 'Il y a 2 min'},
        {'numero': 482090, 'hash': '0000...a2c1', 'txs': 8,  'temps': 'Il y a 14 min'},
        {'numero': 482089, 'hash': '0000...e449', 'txs': 22, 'temps': 'Il y a 25 min'},
        {'numero': 482088, 'hash': '0000...f910', 'txs': 5,  'temps': 'Il y a 38 min'},
        {'numero': 482087, 'hash': '0000...11ab', 'txs': 31, 'temps': 'Il y a 52 min'},
    ]

    alertes_fraude = [
        {'niveau': 'Critique', 'titre': 'Doublon Biométrique Potentiel',
         'description': "Correspondance 98% entre deux empreintes à Labé et Mamou.",
         'id_tx': 'TX_88219'},
        {'niveau': 'Info', 'titre': "Pic d'Activité Anormal",
         'description': "Hausse inhabituelle d'enregistrements sur Conakry Sud.", 'id_tx': ''},
        {'niveau': 'Info', 'titre': 'Modification Hors-Délai',
         'description': "Un acte a été modifié 48h après sa création.", 'id_tx': 'TX_77104'},
    ]

    contexte = {
        'dernier_bloc':     482091,
        'sante_reseau':     99.98,
        'nb_alertes_ia':    3,
        'hash_systeme':     'SHA-256',
        'blocs_recents':    blocs_recents,
        'alertes_fraude':   alertes_fraude,
        'journal':          journal,
        'nb_journal':       nb_journal,
        'filtre_q':         filtre_q,
        'total_actes':      total_actes,
        'actes_sync':       actes_sync,
        'actes_en_attente': actes_en_attente,
        'actes_erreur':     actes_erreur,
        'derniers_actes':   derniers_actes,
    }
    return render(request, 'audits/audit.html', contexte)


@login_required
def vue_analyser_transaction(request, id_tx):
    """Analyse détaillée d'une transaction / acte suspect signalé par l'IA."""
    if not (request.user.est_admin_national or request.user.est_super_admin):
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    from actes.models import ActeNaissance
    from .models import JournalAudit

    # Chercher l'acte par transaction_hash ou reference contenant l'id_tx
    acte = None
    actes_similaires = []

    # Recherche par transaction_hash
    acte = ActeNaissance.objects.filter(transaction_hash__icontains=id_tx).first()

    # Si pas trouvé, chercher par référence
    if not acte:
        acte = ActeNaissance.objects.filter(reference__icontains=id_tx.replace('TX_', '')).first()

    # Si toujours pas trouvé, prendre le dernier acte modifié (cas TX_77104 = modification hors-délai)
    if not acte:
        acte = ActeNaissance.objects.order_by('-date_modification').first()

    # Actes similaires (même agent ou même région)
    if acte:
        actes_similaires = ActeNaissance.objects.filter(
            region_naissance=acte.region_naissance
        ).exclude(pk=acte.pk).order_by('-date_creation')[:5]

    # Journal lié à cet acte
    journal_lie = JournalAudit.objects.filter(
        chemin__icontains=str(acte.pk) if acte else ''
    ).order_by('-horodatage')[:10]

    # Calcul délai de modification
    delai_modification = None
    flag_hors_delai = False
    if acte:
        delai = acte.date_modification - acte.date_creation
        delai_modification = delai
        flag_hors_delai = delai.total_seconds() > 172800  # > 48h

    contexte = {
        'id_tx':             id_tx,
        'acte':              acte,
        'actes_similaires':  actes_similaires,
        'journal_lie':       journal_lie,
        'delai_modification': delai_modification,
        'flag_hors_delai':   flag_hors_delai,
        'analyse_date':      timezone.now(),
    }
    return render(request, 'audits/analyse_transaction.html', contexte)