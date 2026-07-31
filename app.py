from flask import Flask,request,jsonify
from services.weather_service import get_aqi_data
from services.advisory_engine import get_advisory

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
    

@app.route("/api/advisory",methods = ["POST"])
def post_advisory():
    body = request.get_json(silent = True)
    
    if not body:
        return jsonify({"error": "Request body must be valid JSON"}), 400
    
    aqi_category = body.get("aqi_category")
    health_conditions = body.get("health_conditions",[])
    
    if not aqi_category:
        return jsonify({"error": "aqi_category is required"}), 400

    if not isinstance(health_conditions, list):
        return jsonify({"error": "health_conditions must be a list"}), 400

    result = get_advisory(aqi_category, health_conditions)
    return jsonify(result), 200
        




app.run(debug = True)