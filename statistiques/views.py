# ============================================================
# NaissanceChain — Vues Statistiques (maquette page 11)
# ============================================================

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
import csv


@login_required
def vue_statistiques(request):
    if not (request.user.est_admin_national or request.user.est_super_admin
            or request.user.est_admin_prefectoral):
        messages.error(request, "Accès refusé.")
        return redirect('dashboard:index')

    couverture_regions = [
        {'nom': 'CONAKRY',   'taux': 92, 'niveau': 'optimal'},
        {'nom': 'KANKAN',    'taux': 78, 'niveau': 'correct'},
        {'nom': 'LABÉ',      'taux': 65, 'niveau': 'correct'},
        {'nom': 'KINDIA',    'taux': 84, 'niveau': 'optimal'},
        {'nom': 'BOKÉ',      'taux': 58, 'niveau': 'critique'},
        {'nom': 'NZÉRÉKORÉ', 'taux': 71, 'niveau': 'correct'},
        {'nom': 'FARANAH',   'taux': 49, 'niveau': 'critique'},
        {'nom': 'MAMOU',     'taux': 62, 'niveau': 'critique'},
    ]

    zones_risque = [
        {'nom': 'Gaoual Rural',    'taux': 22, 'niveau': 'CRITICAL'},
        {'nom': 'Tougué Sud',      'taux': 29, 'niveau': 'STABLE'},
        {'nom': 'Mandiana Est',    'taux': 34, 'niveau': 'WARNING'},
        {'nom': 'Kérouané Nord',   'taux': 38, 'niveau': 'WARNING'},
        {'nom': 'Yomou Frontière', 'taux': 41, 'niveau': 'NOTICE'},
    ]

    flux_evenements = [
        {'icone': 'fa-database',    'texte': '542 actes synchronisés',     'temps': 'Il y a 2 min'},
        {'icone': 'fa-user-plus',   'texte': 'Nouvel agent déployé à…',    'temps': 'Il y a 15 min'},
        {'icone': 'fa-triangle-exclamation', 'texte': 'Baisse activité détectée', 'temps': 'Il y a 1h'},
        {'icone': 'fa-circle-check','texte': 'Cap 500k naissances atteint','temps': 'Il y a 3h'},
    ]

    contexte = {
        'taux_national':       74.2,
        'total_naissances':    512894,
        'taux_synchronisation': 99.8,
        'zones_en_alerte':     14,
        'couverture_regions':  couverture_regions,
        'zones_risque':        zones_risque,
        'flux_evenements':     flux_evenements,
        'dernier_bloc':        '847,219-BC',
    }
    return render(request, 'statistiques/statistiques.html', contexte)


@login_required
def vue_export_csv(request):
    """Export CSV des statistiques nationales"""
    if not (request.user.est_admin_national or request.user.est_super_admin
            or request.user.est_admin_prefectoral):
        return redirect('dashboard:index')

    from actes.models import ActeNaissance, StatutSynchronisation
    from agents.models import Agent
    from accounts.models import RegionGuinee

    # 1. Optimisation globale : Une seule requête pour toutes les stats régionales
    stats_reg = ActeNaissance.objects.values('agent__utilisateur__region').annotate(
        total=Count('id'),
        sync=Count('id', filter=Q(statut_sync=StatutSynchronisation.SYNCHRONISE)),
        attente=Count('id', filter=Q(statut_sync=StatutSynchronisation.EN_ATTENTE))
    )
    # Conversion en dictionnaire pour un accès rapide : { 'conakry': {...}, ... }
    stats_map = { s['agent__utilisateur__region']: s for s in stats_reg }

    now = timezone.now()
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="rapport_naissancechain_{now.strftime("%Y%m%d_%H%M")}.csv"'
    response.write('\ufeff')  # BOM UTF-8 pour Excel

    writer = csv.writer(response, delimiter=';')

    # En-tete du rapport
    writer.writerow(['RAPPORT NATIONAL NAISSANCECHAIN'])
    writer.writerow([f'Genere le : {now.strftime("%d/%m/%Y a %H:%M")}'])
    writer.writerow([f'Par : {request.user.get_nom_complet()} ({request.user.get_role_display()})'])
    writer.writerow([])

    # 2. Utilisation de agrégations globales pour éviter des counts séparés
    # Stats globales
    writer.writerow(['=== STATISTIQUES GLOBALES ==='])
    writer.writerow(['Indicateur', 'Valeur'])
    writer.writerow(['Total actes enregistres', ActeNaissance.objects.count()])
    writer.writerow(['Actes synchronises blockchain', ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.SYNCHRONISE).count()])
    writer.writerow(['Actes en attente', ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.EN_ATTENTE).count()])
    writer.writerow(['Actes en erreur', ActeNaissance.objects.filter(statut_sync=StatutSynchronisation.ERREUR).count()])
    writer.writerow(['Total agents actifs', Agent.objects.filter(statut='actif').count()])
    writer.writerow(['Agents en ligne', Agent.objects.filter(statut='actif', est_en_ligne=True).count()])
    writer.writerow([])

    # Stats par region
    writer.writerow(['=== STATISTIQUES PAR REGION ==='])
    writer.writerow(['Region', 'Total Actes', 'Synchronises', 'En Attente', 'Taux Sync (%)'])
    for valeur, label in RegionGuinee.choices:
        reg_data = stats_map.get(valeur, {'total': 0, 'sync': 0, 'attente': 0})
        total = reg_data['total']
        sync = reg_data['sync']
        attente = reg_data['attente']
        taux = round(sync / total * 100, 1) if total > 0 else 0
        writer.writerow([label, total, sync, attente, taux])
    writer.writerow([])

    # Derniers actes
    writer.writerow(['=== DERNIERS ACTES ENREGISTRES (20) ==='])
    writer.writerow(['Reference', 'UUID Enfant', 'Nom Enfant', 'Prenom', 'Date Naissance', 'Region', 'Agent', 'Statut', 'Date Creation'])
    for acte in ActeNaissance.objects.select_related('agent__utilisateur').order_by('-date_creation')[:20]:
        writer.writerow([
            acte.reference,
            str(acte.uuid_enfant),
            acte.nom_enfant,
            acte.prenom_enfant,
            acte.date_naissance.strftime('%d/%m/%Y'),
            acte.region_naissance,
            acte.agent.get_nom_complet(),
            acte.get_statut_sync_display(),
            acte.date_creation.strftime('%d/%m/%Y %H:%M'),
        ])

    return response