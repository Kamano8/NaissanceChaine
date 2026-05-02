import hashlib
import json
import random
from django.utils import timezone


def synchroniser_acte(acte):
    """
    Mode simulation : calcule un hash SHA-256 local et marque l'acte comme synchronisé.
    Aucune connexion blockchain réelle requise.
    """
    from .models import StatutSynchronisation

    try:
        donnees = {
            'reference':      acte.reference,
            'nom_enfant':     acte.nom_enfant,
            'prenom_enfant':  acte.prenom_enfant,
            'date_naissance': str(acte.date_naissance),
            'sexe':           acte.sexe,
            'lieu_naissance': acte.lieu_naissance,
            'nom_pere':       acte.nom_pere,
            'nom_mere':       acte.nom_mere,
            'agent_code':     acte.agent.code_agent,
            'date_creation':  str(acte.date_creation),
        }

        contenu       = json.dumps(donnees, sort_keys=True, ensure_ascii=False)
        hash_local    = hashlib.sha256(contenu.encode('utf-8')).hexdigest()

        acte.hash_blockchain  = hash_local
        acte.statut_sync      = StatutSynchronisation.SYNCHRONISE
        acte.index_bloc       = random.randint(480000, 490000)
        acte.transaction_hash = f"0x{hash_local[:62]}"
        acte.date_sync        = timezone.now()

        acte.save(update_fields=[
            'hash_blockchain', 'statut_sync', 'index_bloc',
            'transaction_hash', 'date_sync'
        ])

    except Exception as e:
        from .models import StatutSynchronisation
        acte.statut_sync = StatutSynchronisation.ERREUR
        acte.save(update_fields=['statut_sync'])


def verifier_acte_blockchain(reference: str, hash_fourni: str) -> dict:
    """Vérifie l'authenticité d'un acte via son hash."""
    from .models import ActeNaissance

    try:
        acte = ActeNaissance.objects.get(reference=reference)
    except ActeNaissance.DoesNotExist:
        return {'valide': False, 'raison': 'Acte introuvable dans le registre'}

    if not acte.est_synchronise:
        return {'valide': False, 'raison': 'Acte non encore synchronisé'}

    if acte.hash_blockchain == hash_fourni:
        return {
            'valide':    True,
            'acte':      acte,
            'hash':      acte.hash_blockchain,
            'bloc':      acte.index_bloc,
            'date_sync': acte.date_sync,
        }

    return {'valide': False, 'raison': 'Hash invalide — document potentiellement falsifié'}
