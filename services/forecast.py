import pandas as pd
from database.supabase_client import get_aqi_history

def get_forcast(city:str,min_data_points: int = 12)->dict:
    
    history = get_aqi_history(city,limit = 500)
    if len(history) < min_data_points:
        return{
            "status": "insufficient_data",
            "message": f"Still collecting historical data for {city}. "
                       f"Have {len(history)} readings, need at least {min_data_points} for a reliable trend.",
            "data_points": len(history)
        }
        
    df = pd.DataFrame(history)
    df["recorder_at"] = pd.to_datetime(df["recorder_at"])
    df = df.sort_values("recorder_at")
    
    half = df(len)//2
    older_avg = df.iloc[:half]['aqi_us'].mean()
    recent_avg = df.iloc[half:]['aqi_us'].mean()
    
    diff = recent_avg - older_avg
    if diff > 5:
        trend_direction = "rising"
    elif diff < -5:
        trend_direction = "falling"
    else:
        trend_direction = "stable"
        
    df['hour'] = df['recorded_at'].dt.hour
    hourly_avg = df.groupby('hour')['aqi_us'].mean().round(1)

    worst_hour = int(hourly_avg.idxmax())
    best_hour = int(hourly_avg.idxmin())
    
    latest_reading = df.iloc[-1]['aqi_us']
    trend_adjustment = (recent_avg - older_avg) * 0.3  # damped, avoid wild swings
    estimated_next_24h = round(latest_reading + trend_adjustment)
    estimated_next_24h = max(0, min(estimated_next_24h, 500))  # keep in valid AQI range

    return {
        "status": "ok",
        "data_points": len(df),
        "trend_direction": trend_direction,
        "recent_avg_aqi": round(recent_avg, 1),
        "older_avg_aqi": round(older_avg, 1),
        "worst_hour_of_day": worst_hour,
        "best_hour_of_day": best_hour,
        "current_aqi": int(latest_reading),
        "estimated_next_24h_aqi": estimated_next_24h
    }