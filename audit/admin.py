from django.contrib import admin
from .models import JournalAudit

@admin.register(JournalAudit)
class JournalAuditAdmin(admin.ModelAdmin):
    list_display = ('horodatage', 'utilisateur', 'action', 'adresse_ip', 'statut_http')
    list_filter = ('methode', 'statut_http', 'region')
    search_fields = ('utilisateur__email', 'action', 'adresse_ip')
    readonly_fields = ('utilisateur', 'action', 'chemin', 'methode', 'adresse_ip', 'statut_http', 'region', 'horodatage')
    
    def has_add_permission(self, request): return False
