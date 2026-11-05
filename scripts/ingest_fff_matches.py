
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse


# 1. Configuration de la source
BASE_URL = "https://api-dofa.fff.fr"

ENDPOINT = "/api/compets/451348/phases/1/poules/1/resultat"

FIRST_URL = (
    f"{BASE_URL}{ENDPOINT}"
    "?ma_dat%5Bafter%5D=2026-08-01"
    "&ma_dat%5Bbefore%5D=2027-06-30"
)

# Configuration HTTP utilisée lors de nos tests
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

HEADERS = [
    "Accept: application/json, text/plain, */*",
    "Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    'Sec-CH-UA: "Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-CH-UA-Mobile: ?0",
    'Sec-CH-UA-Platform: "Windows"',
    "Sec-Fetch-Dest: empty",
    "Sec-Fetch-Mode: cors",
    "Sec-Fetch-Site: same-site",
    "Origin: https://www.fff.fr",
    "Referer: https://www.fff.fr/",
]


# 2. Fonction de récupération HTTP
def fetch_page(url):
    parsed = urlparse(url)

    # N'accepter que l'endpoint attendu
    if (
        parsed.scheme != "https"
        or parsed.netloc != "api-dofa.fff.fr"
        or parsed.path != ENDPOINT
    ):
        raise ValueError(f"URL inattendue : {url}")

    command = [
        "curl",
        "--http2",
        "--compressed",
        "-sS",
        "-L",
        "--fail",
        "--max-time", "20",
        "-A", USER_AGENT,
    ]

    for header in HEADERS:
        command.extend(["-H", header])

    command.append(url)

    result = subprocess.run(
        command,
        capture_output=True,
        check=True,
        timeout=30,
    )

    return json.loads(result.stdout), result.stdout


# 3. Pipeline d'ingestion
def main():
    print("Début de l'ingestion des matchs FFF")

    next_url = FIRST_URL
    visited_urls = set()
    all_matches = []
    seen_ids = set()
    raw_pages = []
    expected_total = None

    while next_url:
        if next_url in visited_urls:
            raise ValueError("Boucle de pagination détectée")

        if len(raw_pages) >= 10:
            raise ValueError("Limite de 10 pages atteinte")

        visited_urls.add(next_url)

        data, raw_response = fetch_page(next_url)

        if not isinstance(data, dict):
            raise ValueError("Réponse JSON inattendue")

        matches = data.get("hydra:member")

        if not isinstance(matches, list):
            raise ValueError("Collection de matchs absente")

        if expected_total is None:
            expected_total = data.get("hydra:totalItems")

        # Validation et consolidation
        for match in matches:
            match_id = match.get("ma_no")

            if match_id is None:
                raise ValueError("Match sans identifiant")

            if match_id in seen_ids:
                raise ValueError(f"Doublon détecté : {match_id}")

            seen_ids.add(match_id)
            all_matches.append(match)

        raw_pages.append(raw_response)

        print(
            f"Page {len(raw_pages)} : "
            f"{len(matches)} matchs récupérés"
        )

        # Lecture du lien vers la page suivante
        view = data.get("hydra:view") or {}
        next_path = view.get("hydra:next")

        next_url = (
            urljoin(BASE_URL, next_path)
            if next_path else None
        )

        # Temporisation entre les requêtes
        if next_url:
            time.sleep(1)

    # Vérification de la complétude
    if expected_total != len(all_matches):
        raise ValueError(
            f"Ingestion incomplète : "
            f"{len(all_matches)}/{expected_total} matchs"
        )

    # 4. Sauvegarde des données
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    output_dir = (
        Path("data/raw/fff/matches")
        / f"451348_phase1_poule1_{timestamp}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # Conservation des réponses originales
    for index, raw_page in enumerate(raw_pages, start=1):
        path = output_dir / f"page_{index:02}.json"
        path.write_bytes(raw_page)

    # Création d'un fichier consolidé
    output_file = output_dir / "matches.json"

    output_file.write_text(
        json.dumps(all_matches, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\n=== INGESTION TERMINÉE ===")
    print(f"Pages téléchargées : {len(raw_pages)}")
    print(f"Matchs uniques : {len(all_matches)}")
    print(f"Fichier consolidé : {output_file}")


if __name__ == "__main__":
    try:
        main()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        json.JSONDecodeError,
        ValueError,
    ) as error:
        print(f"Échec de l'ingestion : {error}")
        raise SystemExit(1) from error
