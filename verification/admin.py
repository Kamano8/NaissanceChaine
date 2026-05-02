from django.contrib import admin
from django.utils.html import format_html
from .models import DemandeActe


@admin.register(DemandeActe)
class DemandeActeAdmin(admin.ModelAdmin):
    list_display  = ['id', 'citoyen', 'nom_complet_enfant', 'date_naissance', 'statut_badge', 'date_creation']
    list_filter   = ['statut', 'date_creation']
    search_fields = ['nom_enfant', 'prenom_enfant', 'citoyen__email', 'reference_acte']
    ordering      = ['-date_creation']
    readonly_fields = ['citoyen', 'nom_enfant', 'prenom_enfant', 'date_naissance',
                       'lieu_naissance', 'reference_acte', 'motif', 'date_creation']

    fieldsets = (
        ('Citoyen', {
            'fields': ('citoyen',)
        }),
        ("Informations sur l'enfant", {
            'fields': ('nom_enfant', 'prenom_enfant', 'date_naissance', 'lieu_naissance', 'reference_acte')
        }),
        ('Demande', {
            'fields': ('motif', 'date_creation')
        }),
        ('Traitement (Admin)', {
            'fields': ('statut', 'commentaire_admin', 'acte_lie')
        }),
    )

    def nom_complet_enfant(self, obj):
        return f"{obj.prenom_enfant} {obj.nom_enfant}"
    nom_complet_enfant.short_description = "Enfant"

    def statut_badge(self, obj):
        couleurs = {
            'en_attente': '#fd7e14',
            'en_cours':   '#0d6efd',
            'approuvee':  '#198754',
            'rejetee':    '#dc3545',
        }
        couleur = couleurs.get(obj.statut, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            couleur, obj.get_statut_display()
        )
    statut_badge.short_description = "Statut"
