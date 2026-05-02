import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(username='admin', email='admin@naissancechain.gn', password='Admin2026@')
    print("Superuser cree avec succes !")
else:
    print("Superuser existe deja.")
