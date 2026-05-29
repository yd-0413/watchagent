import logging

import certifi
import requests
from requests.exceptions import SSLError
import urllib3

from app.config import CITIES

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

logger = logging.getLogger(__name__)


def fetch_current_weather(city_name: str) -> dict:
    if city_name not in CITIES:
        raise ValueError(f"Unknown city: {city_name}")

    city = CITIES[city_name]

    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "current": "temperature_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code",
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params=params,
            timeout=10,
            verify=certifi.where(),
        )
    except SSLError:
        logger.warning(
            "SSL certificate verification failed for %s. Retrying without verification for local development.",
            city_name,
        )
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.get(
            OPEN_METEO_URL,
            params=params,
            timeout=10,
            verify=False,
        )

    response.raise_for_status()
    current = response.json()["current"]

    return {
        "city": city_name,
        "timestamp": current["time"],
        "temperature_2m": current["temperature_2m"],
        "apparent_temperature": current["apparent_temperature"],
        "precipitation": current["precipitation"],
        "wind_speed_10m": current["wind_speed_10m"],
        "weather_code": current["weather_code"],
    }