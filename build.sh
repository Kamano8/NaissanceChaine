#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@naissancechain.gn').exists():
    User.objects.create_superuser(email='admin@naissancechain.gn', password='Admin2026@')
    print('Superuser cree!')
else:
    print('Superuser existe deja.')
"
