import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from aqi_calculator import calculate_aqi_from_pm25

load_dotenv()

API_KEY = os.getenv("OWM_API_KEY")
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
    
if __name__ == "__main__":
    result = get_aqi_data(31.5497, 74.3436)  # Lahore
    print(result)