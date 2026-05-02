from .models import AlerteZone
from django.core.cache import cache


def alertes_navbar(request):
    """
    Injecte les alertes actives dans toutes les pages.
    Utilise un cache de 5 minutes pour éviter des requêtes SQL répétitives.
    """
    if not request.user.is_authenticated:
        return {'alertes_navbar': [], 'nb_alertes_navbar': 0}

    cache_key = 'navbar_alerts_active'
    alertes = cache.get(cache_key)
    
    if alertes is None:
        alertes = list(AlerteZone.objects.filter(est_active=True).order_by('-date_creation')[:8])
        cache.set(cache_key, alertes, 300)  # Cache 5 minutes

    return {
        'alertes_navbar': alertes,
        'nb_alertes_navbar': len(alertes),
    }
