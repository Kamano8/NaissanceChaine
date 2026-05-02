from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.vue_dashboard, name='index'),
    path('utilisateurs/', views.vue_utilisateurs, name='utilisateurs'),
    path('utilisateurs/creer/', views.vue_creer_utilisateur, name='creer_utilisateur'),
    path('utilisateurs/<int:pk>/toggle/', views.vue_toggle_utilisateur, name='toggle_utilisateur'),
    path('utilisateurs/<int:pk>/supprimer/', views.vue_supprimer_utilisateur, name='supprimer_utilisateur'),
]