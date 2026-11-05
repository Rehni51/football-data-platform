import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Configuration
URL = "https://api-dofa.fff.fr/api/clubs.json?filter=Reims"

# Commande HTTP : reprise de notre test curl fonctionnel
command = [
    "curl",
    "--http2",
    "--compressed",
    "--silent",
    "--show-error",
    "--location",
    "--fail",
    "--max-time", "20",
    "--user-agent",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36",
    "--header", "Accept: application/json, text/plain, */*",
    "--header", "Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "--header", 'Sec-CH-UA: "Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "--header", "Sec-CH-UA-Mobile: ?0",
    "--header", 'Sec-CH-UA-Platform: "Windows"',
    "--header", "Sec-Fetch-Dest: empty",
    "--header", "Sec-Fetch-Mode: cors",
    "--header", "Sec-Fetch-Site: same-site",
    "--header", "Origin: https://www.fff.fr",
    "--header", "Referer: https://www.fff.fr/",
    URL,
]

print("Début de l'ingestion FFF...")

try:
    # Exécution de curl depuis Python
    result = subprocess.run(
        command,
        capture_output=True,
        check=True,
        timeout=30,
    )

    # Conversion de la réponse en objet Python
    data = json.loads(result.stdout)

    # Vérification du format attendu
    if not isinstance(data, list):
        raise ValueError("La réponse attendue est une liste JSON")

    # Construction du chemin de sauvegarde
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    output_dir = Path("data/raw/fff")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"clubs_reims_{timestamp}.json"

    # Conservation de la réponse brute
    output_file.write_bytes(result.stdout)

    print(f"Nombre de clubs récupérés : {len(data)}")
    print(f"Fichier enregistré : {output_file}")

    # Aperçu limité aux noms et identifiants
    for club in data[:3]:
        print(f"- {club.get('cl_no')} : {club.get('name')}")

except subprocess.CalledProcessError as error:
    print(f"Erreur curl : {error.stderr.decode(errors='replace')}")

except (ValueError, json.JSONDecodeError) as error:
    print(f"Erreur de validation : {error}")

except subprocess.TimeoutExpired:
    print("La requête a dépassé le délai autorisé.")
