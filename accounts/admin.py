# ============================================================
# NaissanceChain — Administration Django pour les utilisateurs
# ============================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    """Interface d'administration personnalisée pour NaissanceChain"""

    list_display  = ['get_nom_complet', 'email', 'role_badge', 'region', 'is_active', 'date_joined']
    list_filter   = ['role', 'region', 'is_active', 'is_staff']
    search_fields = ['email', 'nom', 'prenom', 'identifiant_agent']
    ordering      = ['-date_joined']

    fieldsets = (
        ('Identité', {
            'fields': ('email', 'nom', 'prenom', 'telephone', 'photo')
        }),
        ('Rôle & Affectation', {
            'fields': ('role', 'region', 'prefecture', 'identifiant_agent')
        }),
        ('Sécurité', {
            'fields': ('password', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Audit', {
            'fields': ('date_joined', 'last_login', 'derniere_connexion_ip'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        ('Créer un utilisateur', {
            'classes': ('wide',),
            'fields':  ('email', 'nom', 'prenom', 'role', 'region', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login', 'derniere_connexion_ip']

    def role_badge(self, obj):
        """Affiche le rôle avec un badge coloré"""
        couleurs = {
            'super_admin':       '#dc3545',
            'admin_national':    '#fd7e14',
            'admin_prefectoral': '#0d6efd',
            'agent':             '#198754',
            'citoyen':           '#6c757d',
        }
        couleur = couleurs.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            couleur, obj.get_role_display()
        )
    role_badge.short_description = "Rôle"