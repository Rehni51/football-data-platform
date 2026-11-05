
import json
from pathlib import Path

# 1. Localisation du fichier source
source = Path(
    "data/raw/fff/matches/"
    "451348_phase1_poule1_20261019T154821Z/"
    "matches.json"
)

# 2. Lecture du JSON
matches = json.loads(source.read_text(encoding="utf-8"))

# 3. Préparation des données
prepared_matches = []

for match in matches:
    home = match.get("home") or {}
    away = match.get("away") or {}

    home_club = home.get("club") or {}
    away_club = away.get("club") or {}

    competition = match.get("competition") or {}
    poule = match.get("poule") or {}

    prepared_match = {
        "match_id": match["ma_no"],
        "competition_id": competition.get("cp_no"),
        "season": match.get("season"),
        "poule": poule.get("name"),
        "date": match.get("date"),
        "home_club_id": home_club.get("cl_no"),
        "home_team_number": home.get("number"),
        "home_team": home.get("short_name"),
        "away_club_id": away_club.get("cl_no"),
        "away_team_number": away.get("number"),
        "away_team": away.get("short_name"),
        "home_score": match.get("home_score"),
        "away_score": match.get("away_score"),
        "updated_at": match.get("external_updated_at"),
    }

    prepared_matches.append(prepared_match)

# 4. Contrôles de qualité
match_ids = [match["match_id"] for match in prepared_matches]

if len(match_ids) != len(set(match_ids)):
    raise ValueError("Des identifiants de matchs sont en doublon")

# 5. Sauvegarde
output_dir = Path("data/processed/fff")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "matches_marne_d2.json"

output_file.write_text(
    json.dumps(prepared_matches, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

# 6. Bilan
matches_with_scores = sum(
    match["home_score"] is not None
    and match["away_score"] is not None
    for match in prepared_matches
)

print("=== PRÉPARATION TERMINÉE ===")
print(f"Nombre de rencontres : {len(prepared_matches)}")
print(f"Rencontres avec scores : {matches_with_scores}")
print(f"Rencontres sans score complet : {len(prepared_matches) - matches_with_scores}")
print(f"Fichier : {output_file}")
print("\nExemple :")
print(json.dumps(prepared_matches[0], ensure_ascii=False, indent=2))
