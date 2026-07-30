# EPA breakpoints for PM2.5: (BP_low, BP_high, AQI_low, AQI_high, category)
PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50, "Good"),
    (12.1, 35.4, 51, 100, "Moderate"),
    (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups"),
    (55.5, 150.4, 151, 200, "Unhealthy"),
    (150.5, 250.4, 201, 300, "Very Unhealthy"),
    (250.5, 500.4, 301, 500, "Hazardous"),
]


def calculate_aqi_from_pm25(pm25: float) -> dict:
    """
    Converts a raw PM2.5 concentration (µg/m³) into a US EPA AQI value (0-500)
    using the standard piecewise linear breakpoint formula.
    """
    # Handle out-of-range values (above the table's max breakpoint)
    if pm25 > 500.4:
        return {"aqi_us": 500, "category": "Hazardous"}

    if pm25 < 0:
        pm25 = 0

    for bp_low, bp_high, aqi_low, aqi_high, category in PM25_BREAKPOINTS:
        if bp_low <= pm25 <= bp_high:
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (pm25 - bp_low) + aqi_low
            return {
                "aqi_us": round(aqi),
                "category": category
            }

    # Fallback — shouldn't be hit given the range checks above
    return {"aqi_us": None, "category": "Unknown"}