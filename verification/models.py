from django.db import models
from django.conf import settings


class StatutDemande(models.TextChoices):
    EN_ATTENTE  = 'en_attente',  'En attente'
    EN_COURS    = 'en_cours',    'En cours de traitement'
    APPROUVEE   = 'approuvee',   'Approuvée'
    REJETEE     = 'rejetee',     'Rejetée'


class DemandeActe(models.Model):
    """
    Demande de copie d'acte de naissance soumise par un citoyen.
    Visible et gérée par l'admin dans le panel d'administration.
    """
    citoyen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='demandes',
        verbose_name="Citoyen"
    )

    # Informations sur l'enfant concerné
    nom_enfant       = models.CharField(max_length=100, verbose_name="Nom de l'enfant")
    prenom_enfant    = models.CharField(max_length=150, verbose_name="Prénom(s) de l'enfant")
    date_naissance   = models.DateField(verbose_name="Date de naissance")
    lieu_naissance   = models.CharField(max_length=200, verbose_name="Lieu de naissance")

    # Référence si déjà connue
    reference_acte   = models.CharField(
        max_length=30, blank=True,
        verbose_name="Référence de l'acte (si connue)"
    )

    # Motif de la demande
    motif = models.TextField(verbose_name="Motif de la demande")

    # Statut et traitement
    statut          = models.CharField(
        max_length=20,
        choices=StatutDemande.choices,
        default=StatutDemande.EN_ATTENTE,
        verbose_name="Statut"
    )
    commentaire_admin = models.TextField(
        blank=True,
        verbose_name="Commentaire de l'administrateur"
    )

    # Acte lié (rempli par l'admin après traitement)
    acte_lie = models.ForeignKey(
        'actes.ActeNaissance',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='demandes',
        verbose_name="Acte de naissance lié"
    )

    date_creation    = models.DateTimeField(auto_now_add=True, verbose_name="Date de la demande")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name        = "Demande d'acte"
        verbose_name_plural = "Demandes d'actes"
        ordering            = ['-date_creation']

    def __str__(self):
        return f"Demande #{self.pk} — {self.prenom_enfant} {self.nom_enfant} ({self.get_statut_display()})"
