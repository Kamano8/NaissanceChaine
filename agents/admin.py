# ============================================================
# NaissanceChain — Administration Django pour l'app Agents
# ============================================================

from django.contrib import admin
from django.utils.html import format_html
from .models import Agent, AlerteZone, EvenementActivite


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    """Administration des agents de terrain"""

    list_display  = [
        'code_agent', 'get_nom_complet', 'secteur',
        'statut_badge', 'taux_sync_blockchain',
        'est_en_ligne', 'derniere_activite'
    ]
    list_filter   = ['statut', 'est_en_ligne', 'utilisateur__region']
    search_fields = ['code_agent', 'utilisateur__nom', 'utilisateur__prenom', 'secteur']
    ordering      = ['-derniere_activite']
    readonly_fields = [
        'date_creation', 'date_modification',
        'latitude_actuelle', 'longitude_actuelle',
        'gps_mis_a_jour_le'
    ]

    fieldsets = (
        ('Identité Opérationnelle', {
            'fields': ('utilisateur', 'code_agent', 'secteur', 'centre_etat_civil')
        }),
        ('Statut & Activité', {
            'fields': ('statut', 'est_en_ligne', 'derniere_activite', 'objectif_hebdomadaire')
        }),
        ('Localisation GPS', {
            'fields': ('latitude_actuelle', 'longitude_actuelle', 'precision_gps', 'gps_mis_a_jour_le'),
            'classes': ('collapse',)
        }),
        ('Performance', {
            'fields': ('taux_sync_blockchain', 'niveau_batterie', 'version_application')
        }),
        ('Système', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )

    def get_nom_complet(self, obj):
        return obj.utilisateur.get_nom_complet()
    get_nom_complet.short_description = "Nom complet"

    def statut_badge(self, obj):
        couleurs = {
            'actif':    ('#198754', '✓ Actif'),
            'suspendu': ('#dc3545', '✗ Suspendu'),
            'conge':    ('#fd7e14', '⏸ Congé'),
            'inactif':  ('#6c757d', '— Inactif'),
        }
        couleur, libelle = couleurs.get(obj.statut, ('#6c757d', obj.statut))
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            couleur, libelle
        )
    statut_badge.short_description = "Statut"


@admin.register(AlerteZone)
class AlerteZoneAdmin(admin.ModelAdmin):
    list_display  = ['titre', 'region', 'type_alerte', 'est_active', 'date_creation']
    list_filter   = ['region', 'est_active', 'type_alerte']
    search_fields = ['titre', 'region']
    filter_horizontal = ['agents_concernes']


@admin.register(EvenementActivite)
class EvenementActiviteAdmin(admin.ModelAdmin):
    list_display  = ['agent', 'type_evt', 'titre', 'est_lu', 'date_creation']
    list_filter   = ['type_evt', 'est_lu']
    search_fields = ['titre', 'agent__code_agent']
    ordering      = ['-date_creation']