from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    path('',                views.vue_index,             name='index'),
    path('public/',         views.vue_portail_public,    name='public'),
    path('suivi/',          views.vue_suivi_demande,     name='suivi'),
    path('outil/',          views.vue_outil_verification, name='outil'),
    path('mes-demandes/',    views.vue_mes_demandes,      name='mes_demandes'),
    path('nouvelle-demande/', views.vue_nouvelle_demande,  name='nouvelle_demande'),
    path('scanner/',          views.vue_scanner_acte,      name='scanner'),
]