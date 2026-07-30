# Advisory messages per health condition, per AQI category
# Based on WHO/EPA air quality health guidance

ADVISORY_RULES = {
    "none": {
        "Good": "Air quality is good. Enjoy outdoor activities as normal.",
        "Moderate": "Air quality is acceptable. Unusually sensitive individuals should consider reducing prolonged outdoor exertion.",
        "Unhealthy for Sensitive Groups": "Air quality is fine for most people, but consider limiting prolonged outdoor exertion.",
        "Unhealthy": "Reduce prolonged or heavy outdoor exertion. Consider wearing a mask outdoors.",
        "Very Unhealthy": "Avoid prolonged outdoor exertion. Limit time outdoors where possible.",
        "Hazardous": "Avoid all outdoor physical activity. Stay indoors with windows closed.",
    },
    "asthma": {
        "Good": "Safe for outdoor activity, including exercise.",
        "Moderate": "Keep your rescue inhaler accessible during outdoor time.",
        "Unhealthy for Sensitive Groups": "Avoid outdoor exercise during traffic peak hours (7-10am, 5-7pm). Keep inhaler accessible.",
        "Unhealthy": "Avoid outdoor exertion. Stay indoors with windows closed. Use preventive inhaler as prescribed.",
        "Very Unhealthy": "Avoid all outdoor exposure. Monitor symptoms closely and seek medical advice if breathing difficulty occurs.",
        "Hazardous": "Stay indoors at all times. Seek medical attention immediately if experiencing breathing difficulty.",
    },
    "elderly": {
        "Good": "Safe for normal outdoor activity.",
        "Moderate": "Generally safe, but reduce prolonged outdoor exertion if you have any heart or lung conditions.",
        "Unhealthy for Sensitive Groups": "Limit prolonged outdoor exertion, especially during midday hours.",
        "Unhealthy": "Stay indoors as much as possible. Avoid outdoor exertion entirely.",
        "Very Unhealthy": "Remain indoors with windows closed. Avoid any outdoor activity.",
        "Hazardous": "Stay indoors at all times. Monitor for symptoms like shortness of breath or chest discomfort.",
    },
    "pregnant": {
        "Good": "Safe for normal outdoor activity.",
        "Moderate": "Generally safe, minor precautions not needed.",
        "Unhealthy for Sensitive Groups": "Consider limiting prolonged outdoor exertion.",
        "Unhealthy": "Limit outdoor exposure where possible. Prolonged exposure to poor air quality is linked to health risks during pregnancy.",
        "Very Unhealthy": "Avoid outdoor exposure. Stay indoors with windows closed.",
        "Hazardous": "Remain indoors at all times. Consult your doctor if you experience unusual symptoms.",
    },
    "child": {
        "Good": "Safe for outdoor play as normal.",
        "Moderate": "Generally safe for outdoor play.",
        "Unhealthy for Sensitive Groups": "Limit prolonged outdoor play, especially vigorous activity.",
        "Unhealthy": "Limit outdoor play. Keep vigorous outdoor activity to a minimum.",
        "Very Unhealthy": "Keep children indoors. Avoid outdoor play entirely.",
        "Hazardous": "Keep children indoors at all times with windows closed.",
    },
}

# Priority order when a person has multiple conditions —
# the most restrictive/urgent condition's advice takes precedence
CONDITION_PRIORITY = ["asthma", "pregnant", "child", "elderly", "none"]


def get_advisory(aqi_category: str, health_conditions: list) -> dict:
    if not health_conditions:
        health_conditions = ["none"]

    # Normalize input
    health_conditions = [c.strip().lower() for c in health_conditions]

    # Sort conditions by priority so the most urgent advice appears first
    sorted_conditions = sorted(
        health_conditions,
        key=lambda c: CONDITION_PRIORITY.index(c) if c in CONDITION_PRIORITY else len(CONDITION_PRIORITY)
    )

    advisories = []
    for condition in sorted_conditions:
        if condition in ADVISORY_RULES and aqi_category in ADVISORY_RULES[condition]:
            advisories.append({
                "condition": condition,
                "advice": ADVISORY_RULES[condition][aqi_category]
            })

    # Risk score: how far into the AQI scale we are, mapped 1-5
    RISK_SCORE_MAP = {
        "Good": 1,
        "Moderate": 2,
        "Unhealthy for Sensitive Groups": 3,
        "Unhealthy": 4,
        "Very Unhealthy": 5,
        "Hazardous": 5,
    }

    return {
        "aqi_category": aqi_category,
        "risk_score": RISK_SCORE_MAP.get(aqi_category, 3),
        "advisories": advisories
    }