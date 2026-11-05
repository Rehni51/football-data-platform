import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.types.json import Jsonb


# Racine de notre projet
ROOT = Path(__file__).resolve().parents[1]

# Chargement des variables d'environnement
load_dotenv(ROOT / ".env")

# Fichier contenant nos 132 matchs préparés
source = ROOT / "data/processed/fff/matches_marne_d2.json"

matches = json.loads(source.read_text(encoding="utf-8"))

if not isinstance(matches, list):
    raise ValueError("Le fichier doit contenir une liste JSON")

# Préparation des données à insérer
rows = [
    (match["match_id"], Jsonb(match))
    for match in matches
]

if len({match_id for match_id, _ in rows}) != len(rows):
    raise ValueError("Identifiants de matchs en doublon")


# Requête d'insertion / mise à jour
query = """
INSERT INTO landing.matches (match_id, payload)
VALUES (%s, %s)

ON CONFLICT (match_id)
DO UPDATE SET
    payload = EXCLUDED.payload,
    ingested_at = NOW()

WHERE landing.matches.payload
    IS DISTINCT FROM EXCLUDED.payload;
"""


# Connexion à PostgreSQL
with psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
) as conn:

    with conn.cursor() as cur:

        # Insertion des rencontres
        cur.executemany(query, rows)

        # Vérification du nombre de rencontres
        cur.execute("SELECT COUNT(*) FROM landing.matches")
        total = cur.fetchone()[0]

print("=== CHARGEMENT TERMINÉ ===")
print(f"Rencontres lues : {len(matches)}")
print(f"Rencontres présentes en base : {total}")
