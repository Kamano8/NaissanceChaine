# ============================================================
# NaissanceChain — Modèle Utilisateur personnalisé
# Gère tous les rôles : Super Admin, Agent, Admin Préfectoral,
# Admin National, Citoyen
# ============================================================

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class RoleChoices(models.TextChoices):
    """Rôles disponibles dans le système NaissanceChain"""
    SUPER_ADMIN       = 'super_admin',       'Super Administrateur'
    ADMIN_NATIONAL    = 'admin_national',    'Administrateur National'
    ADMIN_PREFECTORAL = 'admin_prefectoral', 'Administrateur Préfectoral'
    AGENT             = 'agent',             'Agent de Terrain'
    CITOYEN           = 'citoyen',           'Citoyen'


class RegionGuinee(models.TextChoices):
    """Régions administratives de la République de Guinée"""
    CONAKRY    = 'conakry',    'Conakry'
    KINDIA     = 'kindia',     'Kindia'
    BOKE       = 'boke',       'Boké'
    LABE       = 'labe',       'Labé'
    KANKAN     = 'kankan',     'Kankan'
    FARANAH    = 'faranah',    'Faranah'
    NZEREKORE  = 'nzerekore',  'Nzérékoré'
    MAMOU      = 'mamou',      'Mamou'


class UtilisateurManager(BaseUserManager):
    """Manager personnalisé pour le modèle Utilisateur"""

    def create_user(self, email, password=None, **extra_fields):
        """Crée un utilisateur standard"""
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        utilisateur = self.model(email=email, **extra_fields)
        utilisateur.set_password(password)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_superuser(self, email, password=None, **extra_fields):
        """Crée un super administrateur système"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', RoleChoices.SUPER_ADMIN)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur central de NaissanceChain.
    Remplace le modèle Django par défaut.
    Connexion par email + mot de passe.
    """

    # --- Identité ---
    email        = models.EmailField(unique=True, verbose_name="Adresse email")
    nom          = models.CharField(max_length=100, verbose_name="Nom de famille")
    prenom       = models.CharField(max_length=100, verbose_name="Prénom(s)")
    telephone    = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    photo        = models.ImageField(
        upload_to='photos_utilisateurs/%Y/%m/',
        blank=True, null=True,
        verbose_name="Photo de profil"
    )

    # --- Rôle & Région ---
    role   = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.CITOYEN,
        verbose_name="Rôle"
    )
    region = models.CharField(
        max_length=20,
        choices=RegionGuinee.choices,
        blank=True,
        verbose_name="Région d'affectation"
    )
    prefecture = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Préfecture"
    )

    # --- Identifiant agent (ex: AG-8821) ---
    identifiant_agent = models.CharField(
        max_length=20,
        blank=True, unique=True, null=True,
        verbose_name="Identifiant agent"
    )

    # --- Statut système ---
    is_active    = models.BooleanField(default=True,  verbose_name="Compte actif")
    is_staff     = models.BooleanField(default=False, verbose_name="Accès administration")
    date_joined  = models.DateTimeField(default=timezone.now, verbose_name="Date d'inscription")
    derniere_connexion_ip = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name="Dernière IP de connexion"
    )

    objects = UtilisateurManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    class Meta:
        verbose_name        = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering            = ['-date_joined']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_role_display()})"

    def get_nom_complet(self):
        """Retourne le nom complet formaté"""
        return f"{self.prenom} {self.nom}"

    # --- Vérifications de rôle (utilisées dans les templates et vues) ---
    @property
    def est_super_admin(self):
        return self.role == RoleChoices.SUPER_ADMIN

    @property
    def est_admin_national(self):
        return self.role in [RoleChoices.SUPER_ADMIN, RoleChoices.ADMIN_NATIONAL]

    @property
    def est_admin_prefectoral(self):
        return self.role == RoleChoices.ADMIN_PREFECTORAL

    @property
    def est_agent(self):
        return self.role == RoleChoices.AGENT

    @property
    def est_citoyen(self):
        return self.role == RoleChoices.CITOYEN