from flask import Flask,request,jsonify
from services.weather_service import get_aqi_data
from services.advisory_engine import get_advisory
from database.database import insert_user, get_user
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
        
@app.rpute("/api/users",methods = ["POST"])
def create_user():
    body = request.get_json(silent = True)
    if not body:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        
    name = body.get("name",'').strip().lower()
    age_group = body.get("age_group",'').strip().lower()
    health_conditions = body.get("health_conditions",[]).strip().lower()
    city = body.get('city', '').strip().lower()
    
    if not name:
        return jsonify({"error": "name is required"}), 400
    if age_group not in ['child', 'adult', 'elderly']:
        return jsonify({"error": "age_group must be one of: child, adult, elderly"}), 400
    if city not in CITY_COORDS:
        return jsonify({"error": f"city '{city}' not supported"}), 400
    if not isinstance(health_conditions, list):
        return jsonify({"error": "health_conditions must be a list"}), 400

    conditions_str = ",".join(health_conditions) if health_conditions else "none"

    user_id = insert_user(name, age_group, conditions_str, city)

    return jsonify({"id": user_id, "message": "User profile created"}), 201


@app.route('/api/users/<int:user_id>/advisory', methods=['GET'])
def get_user_advisory(user_id):
    user = get_user(user_id)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    city = user['city']
    lat, lon = CITY_COORDS[city]

    aqi_data = get_aqi_data(lat, lon)
    if aqi_data is None:
        return jsonify({"error": "Failed to fetch live AQI data"}), 502

    health_conditions = user['health_conditions'].split(",") if user['health_conditions'] != "none" else []

    advisory = get_advisory(aqi_data['category'], health_conditions)

    return jsonify({
        "user": {
            "name": user['name'],
            "city": city,
            "health_conditions": health_conditions
        },
        "current_aqi": aqi_data,
        "advisory": advisory
    }), 200

app.run(debug = True)