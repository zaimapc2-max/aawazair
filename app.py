from flask import Flask, request, jsonify
from flask_cors import CORS
from services.weather_service import get_aqi_data, geocode_city
from services.advisory_engine import get_advisory
from database.database import insert_user, get_user, init_db
from database.supabase_client import add_tracked_city
from apscheduler.schedulers.background import BackgroundScheduler
from scripts.collect_hourly import collect
import os


init_db()
app = Flask(__name__)
CORS(app)

scheduler = BackgroundScheduler()
scheduler.add_job(collect, 'interval', hours=1)
scheduler.start()

@app.route('/api/aqi', methods=['GET'])
def get_aqi():
    city = request.args.get('city', '').strip()
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    location = geocode_city(city)
    if location is None:
        return jsonify({"error": f"Could not find city '{city}'"}), 404

    data = get_aqi_data(location['lat'], location['lon'])
    if data is None:
        return jsonify({"error": "Failed to fetch AQI data"}), 502

    add_tracked_city(location['resolved_name'])  # <-- new line

    data["city"] = location['resolved_name']
    data["country"] = location['country']
    return jsonify(data), 200
    

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
        
@app.route('/api/users', methods=['POST'])
def create_user():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    name = body.get('name', '').strip()
    age_group = body.get('age_group', '').strip().lower()
    health_conditions = body.get('health_conditions', [])
    city = body.get('city', '').strip()

    if not name:
        return jsonify({"error": "name is required"}), 400
    if age_group not in ['child', 'adult', 'elderly']:
        return jsonify({"error": "age_group must be one of: child, adult, elderly"}), 400
    if not city:
        return jsonify({"error": "city is required"}), 400
    if not isinstance(health_conditions, list):
        return jsonify({"error": "health_conditions must be a list"}), 400

    # Validate the city actually resolves to a real place before saving
    location = geocode_city(city)
    if location is None:
        return jsonify({"error": f"Could not find city '{city}'"}), 400

    conditions_str = ",".join(health_conditions) if health_conditions else "none"
    user_id = insert_user(name, age_group, conditions_str, location['resolved_name'])

    return jsonify({"id": user_id, "message": "User profile created", "resolved_city": location['resolved_name']}), 201


@app.route('/api/users/<int:user_id>/advisory', methods=['GET'])
def get_user_advisory(user_id):
    user = get_user(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    location = geocode_city(user['city'])
    if location is None:
        return jsonify({"error": "Could not resolve saved city"}), 502

    aqi_data = get_aqi_data(location['lat'], location['lon'])
    if aqi_data is None:
        return jsonify({"error": "Failed to fetch live AQI data"}), 502

    health_conditions = user['health_conditions'].split(",") if user['health_conditions'] != "none" else []
    advisory = get_advisory(aqi_data['category'], health_conditions)

    return jsonify({
        "user": {"name": user['name'], "city": user['city'], "health_conditions": health_conditions},
        "current_aqi": aqi_data,
        "advisory": advisory
    }), 200

    
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed on this endpoint"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)