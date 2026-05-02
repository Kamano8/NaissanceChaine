# ============================================================
# NaissanceChain — Modèles de l'app Agents
# Représente les agents de terrain qui enregistrent les actes
# ============================================================

from django.db import models
from django.conf import settings
from django.utils import timezone


class StatutAgent(models.TextChoices):
    """Statuts possibles d'un agent de terrain"""
    ACTIF     = 'actif',     'Actif'
    SUSPENDU  = 'suspendu',  'Suspendu'
    CONGE     = 'conge',     'En congé'
    INACTIF   = 'inactif',   'Inactif'


class Agent(models.Model):
    """
    Profil complet d'un agent de terrain NaissanceChain.
    Un agent est lié à un compte Utilisateur de rôle 'agent'.
    Il opère dans une zone géographique définie (région / préfecture).
    """

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil_agent',
        verbose_name="Compte utilisateur"
    )

    # --- Identité opérationnelle ---
    code_agent  = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code agent (ex: AG-8821)"
    )
    secteur     = models.CharField(
        max_length=150,
        verbose_name="Secteur d'intervention (ex: Kindia Centre)"
    )
    centre_etat_civil = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Centre d'état civil rattaché"
    )

    # --- Statut & Activité ---
    statut          = models.CharField(
        max_length=20,
        choices=StatutAgent.choices,
        default=StatutAgent.ACTIF,
        verbose_name="Statut"
    )
    est_en_ligne    = models.BooleanField(default=False, verbose_name="En ligne")
    derniere_activite = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Dernière activité"
    )

    # --- Localisation GPS ---
    latitude_actuelle  = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True,
        verbose_name="Latitude GPS actuelle"
    )
    longitude_actuelle = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True,
        verbose_name="Longitude GPS actuelle"
    )
    precision_gps      = models.IntegerField(
        null=True, blank=True,
        verbose_name="Précision GPS (en mètres)"
    )
    gps_mis_a_jour_le  = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Dernière mise à jour GPS"
    )

    # --- Performance ---
    objectif_hebdomadaire = models.IntegerField(
        default=50,
        verbose_name="Objectif hebdomadaire (actes)"
    )
    taux_sync_blockchain  = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=0.00,
        verbose_name="Taux de synchronisation blockchain (%)"
    )

    # --- Équipement ---
    niveau_batterie    = models.IntegerField(
        null=True, blank=True,
        verbose_name="Niveau de batterie du terminal (%)"
    )
    version_application = models.CharField(
        max_length=20,
        default='1.0.0',
        verbose_name="Version de l'application"
    )

    # --- Dates système ---
    date_creation      = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification  = models.DateTimeField(auto_now=True,     verbose_name="Dernière modification")

    class Meta:
        verbose_name        = "Agent de terrain"
        verbose_name_plural = "Agents de terrain"
        ordering            = ['-derniere_activite']

    def __str__(self):
        return f"{self.utilisateur.get_nom_complet()} ({self.code_agent}) — {self.secteur}"

    def get_nom_complet(self):
        return self.utilisateur.get_nom_complet()

    @property
    def actes_aujourd_hui(self):
        """Nombre d'actes enregistrés aujourd'hui par cet agent"""
        from actes.models import ActeNaissance
        aujourd_hui = timezone.now().date()
        return ActeNaissance.objects.filter(
            agent=self,
            date_creation__date=aujourd_hui
        ).count()

    @property
    def actes_non_synchronises(self):
        """Nombre d'actes en attente de synchronisation blockchain"""
        from actes.models import ActeNaissance, StatutSynchronisation
        return ActeNaissance.objects.filter(
            agent=self,
            statut_sync=StatutSynchronisation.EN_ATTENTE
        ).count()


class AlerteZone(models.Model):
    """
    Alerte géographique envoyée à un ou plusieurs agents.
    Visible dans le flux d'activité de l'agent concerné.
    """

    TypeAlerte = models.TextChoices(
        'TypeAlerte',
        'SECURITE TECHNIQUE ADMINISTRATIVE INFO'
    )

    titre       = models.CharField(max_length=200, verbose_name="Titre de l'alerte")
    description = models.TextField(verbose_name="Description")
    region      = models.CharField(max_length=50,  verbose_name="Région concernée")
    type_alerte = models.CharField(
        max_length=20,
        default='SECURITE',
        verbose_name="Type d'alerte"
    )
    est_active  = models.BooleanField(default=True, verbose_name="Alerte active")
    agents_concernes = models.ManyToManyField(
        Agent,
        related_name='alertes',
        blank=True,
        verbose_name="Agents concernés"
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name        = "Alerte de zone"
        verbose_name_plural = "Alertes de zone"
        ordering            = ['-date_creation']

    def __str__(self):
        return f"[{self.region}] {self.titre}"


class EvenementActivite(models.Model):
    """
    Événement dans le flux d'activité d'un agent.
    Correspond aux cartes du flux de la maquette page 1.
    """

    TypeEvenement = models.TextChoices(
        'TypeEvenement',
        'SYNCHRONISATION MISE_A_JOUR ALERTE_IDENTITE FELICITATION INFO'
    )

    agent       = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='evenements',
        verbose_name="Agent"
    )
    type_evt    = models.CharField(
        max_length=30,
        verbose_name="Type d'événement"
    )
    titre       = models.CharField(max_length=200, verbose_name="Titre")
    contenu     = models.TextField(verbose_name="Contenu")
    est_lu      = models.BooleanField(default=False, verbose_name="Lu")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        verbose_name        = "Événement d'activité"
        verbose_name_plural = "Événements d'activité"
        ordering            = ['-date_creation']

    def __str__(self):
        return f"{self.agent.code_agent} — {self.titre}"