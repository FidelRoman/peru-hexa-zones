import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv() 

# Recupera el token
AUTH_TOKEN = os.getenv("RAPPI_AUTH_TOKEN")

# Función para obtener la cobertura
def get_coverage(lat, lng):
    url = f"https://services.rappi.pe/availability/v1/has-coverage?lat={lat}&lng={lng}"

    headers = {
        'Authorization': f"Bearer {AUTH_TOKEN}",
    }

    response = requests.get(url, headers=headers)

    try:
        data = response.json()  # Convertir respuesta a JSON

        return data.get("has_coverage", None), data["cpgs"].get("city", None), data["cpgs"].get("zone", None)

    except json.JSONDecodeError:
        return None, None, None  # En caso de error, devolver valores nulos
    

def get_coverage_updated(lat, lng):
    url = "https://services.rappi.pe/api/web-gateway/web/restaurants-bus/stores/"

    headers = {
        'Authorization': f"Bearer {AUTH_TOKEN}",
        'content-type': 'application/json'
    }

    payload = json.dumps({
        "lat": lat,
        "lng": lng,
        "store_type": "restaurant",
        "store_ids": [
          "1"
        ],
        "is_prime": True,
        "states": [
          "opened",
          "unavailable",
          "closed"
        ],
        "prime_config": {
          "unlimited_shipping": True
        }
      })
    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        data = response.json()
        message = data.get("error", {}).get("message", "No se encontró mensaje de error")
        return message

    except json.JSONDecodeError:
        print("Error: La respuesta no es un JSON válido.")

