from django.contrib import admin
from django.utils.html import format_html
from .models import ActeNaissance


@admin.register(ActeNaissance)
class ActeNaissanceAdmin(admin.ModelAdmin):
    list_display  = ['reference', 'uuid_court', 'nom_complet_enfant', 'date_naissance', 'sexe', 'agent', 'statut_sync', 'date_creation']
    list_filter   = ['statut_sync', 'sexe', 'region_naissance', 'date_creation']
    search_fields = ['reference', 'uuid_enfant', 'nom_enfant', 'prenom_enfant', 'nom_pere', 'nom_mere']
    ordering      = ['-date_creation']
    readonly_fields = ['reference', 'uuid_enfant', 'date_creation', 'date_modification', 'hash_blockchain', 'transaction_hash', 'date_sync']

    fieldsets = (
        ("Identifiants", {
            'fields': ('reference', 'uuid_enfant')
        }),
        ("Enfant", {
            'fields': ('nom_enfant', 'prenom_enfant', 'date_naissance', 'heure_naissance', 'sexe', 'photo_enfant')
        }),
        ("Lieu de naissance", {
            'fields': ('lieu_naissance', 'region_naissance', 'prefecture', 'sous_prefecture')
        }),
        ("Père", {
            'fields': ('nom_pere', 'nin_pere', 'pere_present', 'pere_verifie')
        }),
        ("Mère", {
            'fields': ('nom_mere', 'profession_mere', 'mere_verifiee')
        }),
        ("Agent & Centre", {
            'fields': ('agent', 'centre_etat_civil')
        }),
        ("Blockchain", {
            'fields': ('statut_sync', 'hash_blockchain', 'transaction_hash', 'index_bloc', 'date_sync'),
            'classes': ('collapse',)
        }),
        ("Métadonnées", {
            'fields': ('date_creation', 'date_modification', 'est_brouillon', 'mode_hors_ligne'),
            'classes': ('collapse',)
        }),
    )

    def uuid_court(self, obj):
        return format_html(
            '<span style="font-family:monospace;font-size:11px;background:#f1f5f9;padding:2px 6px;border-radius:4px">{}</span>',
            str(obj.uuid_enfant).upper()[:8] + '...'
        )
    uuid_court.short_description = 'UUID'

    def nom_complet_enfant(self, obj):
        return obj.get_nom_complet_enfant()
    nom_complet_enfant.short_description = 'Enfant'
