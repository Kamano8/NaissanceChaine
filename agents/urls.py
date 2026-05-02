# ============================================================
# NaissanceChain — URLs de l'app Agents
# ============================================================

from django.urls import path
from . import views

app_name = 'agents'

urlpatterns = [
    # Tableau de bord agent de terrain (mobile)
    path('tableau-de-bord/',         views.tableau_de_bord_agent,  name='tableau_de_bord'),
    path('mon-profil/',              views.vue_profil,             name='profil'),
    path('securite/', views.vue_securite, name='securite'),

    # Gestion admin des agents
    path('',                          views.liste_agents,           name='liste'),
    path('creer/',                    views.creer_agent,            name='creer'),
    path('<int:agent_id>/reassigner/', views.reassigner_agent,      name='reassigner'),

    # API AJAX
    path('api/gps/',                  views.mettre_a_jour_gps,      name='api_gps'),
    path('api/flux-lu/',              views.marquer_flux_lu,        name='api_flux_lu'),
    path('<int:agent_id>/statut/',    views.changer_statut_agent,   name='changer_statut'),
]