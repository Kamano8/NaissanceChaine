#!/usr/bin/env python3
import sqlite3
import os
import sys
import hashlib
import base64
import secrets
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
DB = os.path.normpath(DB)

# Configuration du nouvel utilisateur
EMAIL = 'agent1@example.com'
PRENOM = 'Agent'
NOM = 'Test'
PASSWORD = 'Agent@1234'
ROLE = 'agent_terrain'  # correspond aux choix de la migration
REGION = 'conakry'
IDENTIFIANT_AGENT = 'AG-00001'
CODE_ADMIN = ''

ITERATIONS = 260000


def make_pbkdf2_hash(password, iterations=ITERATIONS):
    salt = secrets.token_hex(8)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    hashed = base64.b64encode(dk).decode('utf-8').strip()
    return f"pbkdf2_sha256${iterations}${salt}${hashed}"


if not os.path.exists(DB):
    print('Erreur: base de données introuvable:', DB)
    sys.exit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Récupère la liste des colonnes existantes
cur.execute("PRAGMA table_info('accounts_utilisateur')")
cols_info = cur.fetchall()
cols = [c[1] for c in cols_info]
print('Colonnes existantes:', cols)

# Ajouter colonne code_admin si absente
if 'code_admin' not in cols:
    print('Ajout de la colonne code_admin...')
    cur.execute("ALTER TABLE accounts_utilisateur ADD COLUMN code_admin varchar(20)")
    conn.commit()
    cols.append('code_admin')

# Ajouter colonne is_active si absente (copie depuis est_actif si présent)
if 'is_active' not in cols:
    print('Ajout de la colonne is_active...')
    cur.execute("ALTER TABLE accounts_utilisateur ADD COLUMN is_active integer DEFAULT 1")
    conn.commit()
    cols.append('is_active')
    if 'est_actif' in cols:
        print('Copie des valeurs depuis est_actif vers is_active...')
        cur.execute("UPDATE accounts_utilisateur SET is_active = est_actif WHERE is_active IS NULL")
        conn.commit()

# Prépare les données à insérer selon les colonnes disponibles
now = datetime.utcnow().isoformat(sep=' ', timespec='seconds')
password_hash = make_pbkdf2_hash(PASSWORD)

row = {
    'password': password_hash,
    'last_login': None,
    'is_superuser': 0,
    'email': EMAIL,
    'prenom': PRENOM,
    'nom': NOM,
    'telephone': '',
    'photo_profil': None,
    'role': ROLE,
    'region': REGION,
    'prefecture': '',
    'sous_secteur': '',
    'identifiant_agent': IDENTIFIANT_AGENT,
    'is_active': 1,
    'est_suspendu': 0 if 'est_suspendu' in cols else None,
    'is_staff': 0 if 'is_staff' in cols else 0,
    'date_inscription': now if 'date_inscription' in cols else now,
    'derniere_connexion': None,
    'langue_preferee': 'fr' if 'langue_preferee' in cols else None,
    'code_admin': CODE_ADMIN if 'code_admin' in cols else None,
}

# Build insert with only existing columns
insert_cols = []
insert_vals = []
for k, v in row.items():
    if k in cols:
        insert_cols.append(k)
        insert_vals.append(v)

placeholders = ','.join(['?'] * len(insert_vals))
cols_sql = ','.join(insert_cols)
sql = f"INSERT INTO accounts_utilisateur ({cols_sql}) VALUES ({placeholders})"
print('Executing:', sql)
cur.execute(sql, insert_vals)
conn.commit()
print('Utilisateur créé avec email:', EMAIL)
print('Mot de passe:', PASSWORD)
conn.close()
