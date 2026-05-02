# ============================================================
# NaissanceChain — URLs principales (CORRIGÉ)
# ============================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/',        admin.site.urls),
    path('auth/',         include('accounts.urls',     namespace='accounts')),
    path('agents/',       include('agents.urls',        namespace='agents')),
    path('actes/',        include('actes.urls',         namespace='actes')),
    path('verification/', include('verification.urls',  namespace='verification')),
    path('dashboard/',    include('dashboard.urls',     namespace='dashboard')),
    path('statistiques/', include('statistiques.urls',  namespace='statistiques')),
    path('audit/',        include('audit.urls',         namespace='audit')),

    # Racine → connexion (redirection simple)
    path('', lambda req: redirect('/auth/connexion/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)