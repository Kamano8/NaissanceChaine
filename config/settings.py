# ============================================================
# NaissanceChain — Configuration principale Django
# Plateforme blockchain de gestion des actes de naissance
# République de Guinée — Hackathon National 2026
# ============================================================

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'naissance-chain-secret-key-guinee-2026')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# ---- Applications installées ----
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps NaissanceChain
    'accounts.apps.AccountsConfig',
    'agents.apps.AgentsConfig',
    'actes.apps.ActesConfig',
    'verification.apps.VerificationConfig',
    'dashboard.apps.DashboardConfig',
    'statistiques.apps.StatistiquesConfig',
    'audit.apps.AuditConfig',
    # Librairies tierces
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middleware custom : journal d'audit automatique
    'audit.middleware.AuditMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'agents.context_processors.alertes_navbar',
            ],
        },
    },
]

# NaissanceChaine/config/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---- Modèle utilisateur personnalisé ----
AUTH_USER_MODEL = 'accounts.Utilisateur'

# ---- Authentification ----
LOGIN_URL = 'accounts:connexion'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'accounts:connexion'

# ---- Fichiers statiques (CSS/JS/Images) ----
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ---- Fichiers media (uploads, photos agents, biométrie) ----
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---- Crispy Forms Bootstrap 5 ----
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ---- Langue & Timezone (Guinée) ----
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---- Configuration Blockchain Ethereum ----
BLOCKCHAIN_NODE_URL = os.getenv('BLOCKCHAIN_NODE_URL', 'https://sepolia.infura.io/v3/TON_PROJECT_ID')
BLOCKCHAIN_PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY', '')
BLOCKCHAIN_CONTRACT_ADDRESS = os.getenv('BLOCKCHAIN_CONTRACT_ADDRESS', '')

# ---- Configuration Email (alertes) ----
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'