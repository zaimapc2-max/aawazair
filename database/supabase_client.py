import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


def insert_aqi_reading(city, aqi_us, category, pm25, pm10):
    url = f"{SUPABASE_URL}/rest/v1/aqi_history"
    payload = {
        "city": city,
        "aqi_us": aqi_us,
        "category": category,
        "pm25": pm25,
        "pm10": pm10
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code not in (200, 201):
        print(f"Failed to insert AQI reading: {response.status_code} {response.text}")
    return response.status_code in (200, 201)


def get_aqi_history(city, limit=168):
    url = f"{SUPABASE_URL}/rest/v1/aqi_history"
    params = {
        "city": f"eq.{city}",
        "order": "recorded_at.desc",
        "limit": limit
    }
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    print(f"Failed to fetch AQI history: {response.status_code} {response.text}")
    return []


def add_tracked_city(city):
    url = f"{SUPABASE_URL}/rest/v1/tracked_cities"
    payload = {"city": city}
    # Supabase returns 409 if the unique constraint fails (city already tracked) - that's fine, ignore it
    response = requests.post(url, json=payload, headers=HEADERS)
    return response.status_code in (200, 201, 409)


def get_tracked_cities():
    url = f"{SUPABASE_URL}/rest/v1/tracked_cities"
    params = {"select": "city"}
    response = requests.get(url, params=params, headers=HEADERS)
    if response.status_code == 200:
        return [row["city"] for row in response.json()]
    print(f"Failed to fetch tracked cities: {response.status_code} {response.text}")
    return []