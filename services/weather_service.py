import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from services.aqi_calculator import calculate_aqi_from_pm25

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


def get_aqi_data(lat: float, lon: float) -> dict:
   
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()  
    except requests.exceptions.RequestException as e:
        print(f"Error fetching AQI data: {e}")
        return None

    data = response.json()

    try:
        components = data["list"][0]["components"]
        pm25 = components["pm2_5"]
    except (KeyError, IndexError):
        print("Unexpected API response structure")
        return None

    aqi_result = calculate_aqi_from_pm25(pm25)

    return {
        "aqi_us": aqi_result["aqi_us"],
        "category": aqi_result["category"],
        "pm25": pm25,
        "pm10": components.get("pm10"),
        "no2": components.get("no2"),
        "so2": components.get("so2"),
        "co": components.get("co"),
        "o3": components.get("o3"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
# Simple in-memory cache so repeated requests for the same city
# during your demo/testing don't hit the geocoding API every time
_geocode_cache = {}


def geocode_city(city_name: str) -> dict | None:
    """
    Converts a city name into lat/lon using OpenWeatherMap's free Geocoding API.
    Returns None if the city can't be found or the request fails.
    """
    cache_key = city_name.strip().lower()
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]

    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city_name,
        "limit": 1,
        "appid": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Geocoding error: {e}")
        return None

    results = response.json()

    if not results:
        return None

    result = {
        "lat": results[0]["lat"],
        "lon": results[0]["lon"],
        "resolved_name": results[0]["name"],
        "country": results[0].get("country")
    }

    _geocode_cache[cache_key] = result
    return result

