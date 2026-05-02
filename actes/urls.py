# ============================================================
# NaissanceChain — URLs de l'app Actes
# ============================================================

from django.urls import path
from . import views

app_name = 'actes'

urlpatterns = [
    path('nouveau/',              views.vue_nouveau_acte,    name='nouveau'),
    path('historique/',           views.vue_historique,      name='historique'),
    path('<int:acte_id>/genere/', views.vue_acte_genere,     name='acte_genere'),
    path('<int:acte_id>/',        views.vue_detail_acte,     name='detail'),
    path('<int:acte_id>/pdf/',    views.vue_telecharger_pdf, name='pdf'),
    path('',                      views.vue_historique,      name='index'),
]