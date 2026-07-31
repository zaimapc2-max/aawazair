from flask import Flask,request,jsonify
from services.weather_service import get_aqi_data

CITY_COORDS = {
    "lahore": (31.5497, 74.3436),
    "karachi": (24.8607, 67.0011),
    "islamabad": (33.6844, 73.0479),
    "faisalabad": (31.4504, 73.1350),
    "multan": (30.1575, 71.5249),
}

app = Flask(__name__)
@app.route("/api/aqi",methods = ["GET"])
def home():
    city = request.args.get("city",'').strip().lower()
    
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    if city not in CITY_COORDS:
        return jsonify({"error": f"City '{city}' not supported"}), 404
    
    lat,lon = CITY_COORDS[city]
    data = get_aqi_data(lat,lon)
    
    if data is None:
        return jsonify({"error": "Failed to fetch AQI data"}), 502
    
    data['city'] = city
    return jsonify(data)
    
app.run(debug = True)