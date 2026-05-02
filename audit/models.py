from django.db import models
from django.conf import settings

class JournalAudit(models.Model):
    """
    Stocke les traces de toutes les actions sensibles effectuées
    sur la plateforme pour la conformité et la sécurité.
    """
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actions_audit'
    )
    action      = models.CharField(max_length=255)
    chemin      = models.CharField(max_length=255)
    methode     = models.CharField(max_length=10)
    adresse_ip  = models.GenericIPAddressField()
    statut_http = models.IntegerField()
    region      = models.CharField(max_length=100, blank=True)
    horodatage  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"
        ordering = ['-horodatage']

    def __str__(self):
        user = self.utilisateur.email if self.utilisateur else "Anonyme"
        return f"{self.horodatage} | {user} | {self.action} ({self.statut_http})"
