import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OWM_API_KEY")

LAT = 31.5497   # Lahore
LON = 74.3436

url = "https://api.openweathermap.org/data/2.5/air_pollution"
params = {
    "lat": LAT,
    "lon": LON,
    "appid": API_KEY
}

response = requests.get(url, params=params)

print("Status code:", response.status_code)
print(response.json())