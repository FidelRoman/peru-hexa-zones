import pandas as pd
import requests
import json
import time


# Función para obtener la cobertura
def get_coverage(lat, lng):
    url = f"https://services.rappi.pe/availability/v1/has-coverage?lat={lat}&lng={lng}"

    headers = {
        'Authorization': 'Bearer ft.gAAAAABn_nG4hvin9ciXkjoPL7uBq6puofPOLGSM4fF1z1xSokSiG7pmBMYDYHscXILV6QD-tVTZfw_Wt7BHCDKxx2URD6THpPLTwMCT1DwC0Tg8Py4Cr9sHOa1X91TY4hykUkN8fcqY_vIQ8gSYdPhaSvVLAZqsLgeuQNasw2XqfaZYvRaQOOS20vLnXOMDZ-kkEnem5_qY240Cg3T_ZoOZAvXGEbxYVwoui1I1rg417XdEq_k12itRPLPDzuGKORtu73GL_w1VF8vSlhXyW_Zqia0JuhMVG7X9FPG53i_CZYDPIZuWuAP6GO3fiiJgqVzlt55SnfafzzRPmTb1k8EzV1ni8982sjkqfff0CDD6lVm1ANMIaW47qkoB5wCJSg_GOvpDuZklrUzOBHE_D99cfagKotzbBg=='
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
        'Authorization': 'Bearer ft.gAAAAABn_nG4hvin9ciXkjoPL7uBq6puofPOLGSM4fF1z1xSokSiG7pmBMYDYHscXILV6QD-tVTZfw_Wt7BHCDKxx2URD6THpPLTwMCT1DwC0Tg8Py4Cr9sHOa1X91TY4hykUkN8fcqY_vIQ8gSYdPhaSvVLAZqsLgeuQNasw2XqfaZYvRaQOOS20vLnXOMDZ-kkEnem5_qY240Cg3T_ZoOZAvXGEbxYVwoui1I1rg417XdEq_k12itRPLPDzuGKORtu73GL_w1VF8vSlhXyW_Zqia0JuhMVG7X9FPG53i_CZYDPIZuWuAP6GO3fiiJgqVzlt55SnfafzzRPmTb1k8EzV1ni8982sjkqfff0CDD6lVm1ANMIaW47qkoB5wCJSg_GOvpDuZklrUzOBHE_D99cfagKotzbBg==',
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

