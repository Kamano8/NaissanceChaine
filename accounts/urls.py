from django.urls import path
from . import views

app_name = 'accounts'


urlpatterns = [
    path('connexion/',   views.VueConnexion.as_view(),   name='connexion'),
    path('inscription/',  views.VueInscription.as_view(), name='inscription'),
    path('deconnexion/', views.VueDeconnexion.as_view(), name='deconnexion'),
    path('profil/',      views.vue_profil,               name='profil'),

    # --- Réinitialisation du mot de passe ---
    path('mot-de-passe-oublie/', views.VueMotDePasseOublie.as_view(), name='password_reset'),
    path('mot-de-passe-oublie/envoye/', views.VueMotDePasseOublieEnvoye.as_view(), name='password_reset_done'),
    path('reinitialiser/<uidb64>/<token>/', views.VueMotDePasseReinitialiser.as_view(), name='password_reset_confirm'),
    path('reinitialiser/termine/', views.VueMotDePasseReinitialiseTermine.as_view(), name='password_reset_complete'),
]