
import httpx

# Adresse du service API
BASE_URL = "https://api-dofa.fff.fr"

# Point d'entrée que nous voulons interroger
ENDPOINT = "/api/clubs.json"

# Paramètres de recherche
PARAMS = {"filter": "Reims"}

# Envoi de la requête HTTP
try:
    response = httpx.get(
        f"{BASE_URL}{ENDPOINT}",
        params=PARAMS,
        timeout=15.0,
        headers={"Accept": "application/json"},
    )

    print(f"URL appelée : {response.url}")
    print(f"Code HTTP : {response.status_code}")

    print(f"Type de contenu : {response.headers.get('content-type')}")
    print(f"Serveur : {response.headers.get('server')}")
    print(f"Réponse : {response.text[:500]}")

    # Déclenche une erreur si le serveur retourne un code 4xx ou 5xx
    response.raise_for_status()

    # Conversion de la réponse JSON en objet Python
    data = response.json()

    print(f"Type de données : {type(data).__name__}")

    if isinstance(data, list):
        print(f"Nombre d'éléments : {len(data)}")
        if data:
            print(f"Premier élément : {data[0]}")

    elif isinstance(data, dict):
        print(f"Clés disponibles : {list(data.keys())}")
        print(f"Aperçu : {str(data)[:1000]}")

except httpx.HTTPError as error:
    print(f"Erreur HTTP ou réseau : {error}")
except ValueError as error:
    print(f"Réponse JSON invalide : {error}")
