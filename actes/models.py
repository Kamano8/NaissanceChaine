# ============================================================
# NaissanceChain — Modèles de l'app Actes
# ActeNaissance : enregistrement d'une naissance sur blockchain
# ============================================================

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class StatutSynchronisation(models.TextChoices):
    """Statut de synchronisation avec la blockchain"""
    EN_ATTENTE  = 'en_attente',  'En attente'
    SYNCHRONISE = 'synchronise', 'Synchronisé'
    ERREUR      = 'erreur',      'Erreur'


class Sexe(models.TextChoices):
    MASCULIN  = 'M', 'Masculin'
    FEMININ   = 'F', 'Féminin'


class ActeNaissance(models.Model):
    """
    Acte de naissance enregistré par un agent de terrain.
    Chaque acte est lié à un bloc blockchain via son hash.
    Maquettes : pages 2, 3, 4 du projet Visily.
    """

    # --- Identifiant unique enfant (UUID) ---
    uuid_enfant = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Identifiant unique enfant (UUID)"
    )

    # --- Identifiant unique acte (référence lisible) ---
    reference = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name="Référence (ex: NC-2024-8842)"
    )

    # --- Informations de l'enfant ---
    nom_enfant       = models.CharField(max_length=100, verbose_name="Nom de l'enfant")
    prenom_enfant    = models.CharField(max_length=150, verbose_name="Prénom(s) de l'enfant")
    date_naissance   = models.DateField(verbose_name="Date de naissance")
    heure_naissance  = models.TimeField(null=True, blank=True, verbose_name="Heure de naissance")
    sexe             = models.CharField(max_length=1, choices=Sexe.choices, verbose_name="Sexe")
    photo_enfant     = models.ImageField(
        upload_to='actes/photos_enfants/%Y/%m/',
        null=True, blank=True,
        verbose_name="Photo de l'enfant"
    )

    # --- Lieu de naissance ---
    lieu_naissance   = models.CharField(max_length=200, verbose_name="Lieu de naissance")
    region_naissance = models.CharField(max_length=50,  verbose_name="Région")
    prefecture       = models.CharField(max_length=100, verbose_name="Préfecture")
    sous_prefecture  = models.CharField(max_length=100, blank=True, verbose_name="Sous-préfecture")

    # --- Père ---
    nom_pere              = models.CharField(max_length=200, verbose_name="Nom complet du père")
    nin_pere              = models.CharField(max_length=30, blank=True, verbose_name="NIN du père")
    pere_present          = models.BooleanField(default=False, verbose_name="Père présent lors de la déclaration")
    pere_verifie          = models.BooleanField(default=False, verbose_name="Identité père vérifiée")

    # --- Mère ---
    nom_mere              = models.CharField(max_length=200, verbose_name="Nom complet de la mère")
    profession_mere       = models.CharField(max_length=100, blank=True, verbose_name="Profession de la mère")
    biometrie_mere        = models.ImageField(
        upload_to='actes/biometrie/%Y/%m/',
        null=True, blank=True,
        verbose_name="Empreinte biométrique mère"
    )
    mere_verifiee         = models.BooleanField(default=False, verbose_name="Identité mère vérifiée")

    # --- Géolocalisation de l'enregistrement ---
    latitude_enregistrement  = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True,
        verbose_name="Latitude de l'enregistrement"
    )
    longitude_enregistrement = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True,
        verbose_name="Longitude de l'enregistrement"
    )
    precision_gps            = models.IntegerField(null=True, blank=True, verbose_name="Précision GPS (m)")

    # --- Agent et centre ---
    agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.PROTECT,
        related_name='actes',
        verbose_name="Agent responsable"
    )
    centre_etat_civil = models.CharField(max_length=200, blank=True, verbose_name="Centre d'état civil")

    # --- Blockchain ---
    statut_sync       = models.CharField(
        max_length=20,
        choices=StatutSynchronisation.choices,
        default=StatutSynchronisation.EN_ATTENTE,
        verbose_name="Statut de synchronisation"
    )
    hash_blockchain   = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Hash blockchain"
    )
    index_bloc        = models.BigIntegerField(null=True, blank=True, verbose_name="Index du bloc")
    transaction_hash  = models.CharField(max_length=255, blank=True, verbose_name="Hash de transaction")
    signature_agent   = models.TextField(blank=True, verbose_name="Signature cryptographique agent")
    date_sync         = models.DateTimeField(null=True, blank=True, verbose_name="Date de synchronisation")

    # --- QR Code ---
    qr_code = models.ImageField(
        upload_to='actes/qrcodes/%Y/%m/',
        null=True, blank=True,
        verbose_name="QR Code"
    )

    # --- Métadonnées ---
    est_brouillon   = models.BooleanField(default=False, verbose_name="Sauvegardé en brouillon")
    mode_hors_ligne = models.BooleanField(default=False, verbose_name="Enregistré hors ligne")
    date_creation   = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True,   verbose_name="Dernière modification")

    class Meta:
        verbose_name        = "Acte de naissance"
        verbose_name_plural = "Actes de naissance"
        ordering            = ['-date_creation']

    def __str__(self):
        return f"{self.reference} — {self.prenom_enfant} {self.nom_enfant}"

    def save(self, *args, **kwargs):
        """Génère la référence unique à la création"""
        if not self.reference:
            annee = timezone.now().year
            uid   = str(uuid.uuid4()).upper()[:4]
            count = ActeNaissance.objects.filter(
                date_creation__year=annee
            ).count() + 1
            self.reference = f"NC-{annee}-{count:04d}-{uid}"
        super().save(*args, **kwargs)

    def get_nom_complet_enfant(self):
        return f"{self.prenom_enfant} {self.nom_enfant}"

    @property
    def est_synchronise(self):
        return self.statut_sync == StatutSynchronisation.SYNCHRONISE

    @property
    def est_en_attente(self):
        return self.statut_sync == StatutSynchronisation.EN_ATTENTE