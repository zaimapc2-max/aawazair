import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.weather_service import get_aqi_data, geocode_city
from database.supabase_client import insert_aqi_reading, get_tracked_cities

def collect():
    cities = get_tracked_cities()
    if not cities:
        print("No cities are being tracked yet.")
        return

    for city in cities:
        location = geocode_city(city)
        if location is None:
            print(f"Could not geocode {city}, skipping")
            continue
        data = get_aqi_data(location['lat'], location['lon'])
        if data is None:
            print(f"Failed to fetch AQI for {city}, skipping")
            continue
        success = insert_aqi_reading(city, data['aqi_us'], data['category'], data['pm25'], data['pm10'])
        print(f"{'Logged' if success else 'FAILED to log'} {city}: AQI {data['aqi_us']} ({data['category']})")

if __name__ == "__main__":
    collect()