# AawazAir

**Personalized Air Quality Health Advisor**

Built for the Girls in STEM Global Hackathon — *Global Challenges, Local Solutions*

---

## The Problem

Lahore and much of Punjab routinely experience "hazardous" air quality during smog season, yet public health messaging stays generic — "wear a mask" tells a healthy adult and someone with asthma the exact same thing, when their actual risk and the right response are completely different. Existing AQI apps show a number. They don't tell a parent whether it's safe to send their child outside today, or tell someone with asthma when to avoid exercise.

AawazAir turns a raw AQI number into a **personalized health advisory** — based on your age group and health conditions, using thresholds grounded in WHO/EPA air quality guidance — plus a live-collected historical trend so you can see how air quality has actually been moving in your city, not just right now.

---

## Screenshots

*(add screenshots here before submission)*

---

## Features

- **Live AQI** for any city worldwide, calculated using the real EPA PM2.5-to-AQI breakpoint formula (not just a passthrough of a raw API number)
- **Personalized health advisory** — factors in age group (child/elderly) and health conditions (asthma, pregnant), with prioritized, combined advice when multiple conditions apply
- **7-day trend chart** built from real, automatically-collected historical data — not simulated
- **Multi-city comparison** — check several cities side by side
- **Automatic hourly data collection** via GitHub Actions + Supabase, running independently of whether the app itself is being actively used

---

## Tech Stack

- **Backend:** Python, Flask
- **Data analysis:** Pandas (trend/forecast logic)
- **Databases:** SQLite (local health profiles) + Supabase/Postgres (historical AQI data — chosen so data keeps accumulating 24/7 regardless of whether the local server is running)
- **Automation:** GitHub Actions scheduled workflow, running hourly to collect live AQI data
- **Frontend:** HTML, CSS, vanilla JavaScript, Chart.js
- **External API:** OpenWeatherMap (Air Pollution + Geocoding)

---

## Architecture

```
                    ┌─────────────────────┐
                    │  GitHub Actions     │
                    │  (runs every hour)  │
                    └──────────┬──────────┘
                               │
                               ▼
┌──────────────┐      ┌───────────────┐      ┌──────────────────┐
│OpenWeatherMap│◄────►│ Flask Backend │◄────►│Supabase(Postgres)│
│ (live AQI +  │      │ (app.py)      │      │aqi_history,      │
│  geocoding)  │      │               │      │ racked_cities    │
└──────────────┘      └───────┬───────┘      └──────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  SQLite (local)     │
                    │  users table only   │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │Frontend (HTML/JS)   │
                    │Chart.js, live badge │
                    └─────────────────────┘
```

**Why two databases?** Historical AQI data needs to keep accumulating around the clock, independent of whether anyone has the app open. Supabase, paired with a GitHub Actions scheduled workflow, handles that continuously in the cloud. Local health profiles don't need that — they only matter while someone's actively using the app, so they stay in simple local SQLite.

**Cities are not hardcoded.** Any city a user checks or signs up with is automatically added to `tracked_cities` and starts accumulating real hourly history from that point forward — this is what lets the system scale to any city on Earth with zero code changes.

---

## API Endpoints

### `GET /api/aqi?city={city_name}`
Live AQI for any city worldwide (geocoded dynamically).

**Response (200):**
```json
{
  "aqi_us": 187,
  "category": "Unhealthy",
  "pm25": 62.4,
  "pm10": 95.1,
  "no2": 18.3,
  "so2": 8.7,
  "co": 450.5,
  "o3": 45.2,
  "timestamp": "2026-08-01T05:16:19+00:00",
  "city": "Lahore",
  "country": "PK"
}
```

### `POST /api/advisory`
Personalized advisory given an AQI category and health conditions.

**Body:** `{"aqi_category": "Unhealthy", "health_conditions": ["asthma", "elderly"]}`

### `POST /api/users`
Creates a health profile. **Body:** `{"name": "...", "age_group": "...", "health_conditions": [...], "city": "..."}`

### `GET /api/users/{id}/advisory`
**Hero endpoint** — combines a saved profile with live AQI in one call, including age-group-based conditions (elderly/child).

### `GET /api/forecast?city={city_name}`
Pandas-based trend analysis. Returns `"status": "insufficient_data"` gracefully until enough history exists.

### `GET /api/history?city={city_name}`
Raw hourly historical readings, used to power the trend chart.

---

## Local Setup

```bash
git clone https://github.com/zaimapc2-max/aawazair.git
cd aawazair
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
OPENWEATHER_API_KEY=your_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

Run:
```bash
python app.py
```
Visit `http://127.0.0.1:5000`

---

## Notes / Lessons Learned

- Supabase tables initially had Row Level Security blocking reads/writes via the anon key; RLS was disabled on `aqi_history` and `tracked_cities`, since this data isn't sensitive (no personal user data lives here — health profiles stay in local SQLite).
- Historical data is genuinely, continuously collected in the background via a GitHub Actions cron job — not simulated or seeded — so the trend chart and forecast feature reflect real conditions and get more accurate the longer the system runs.

---

## Future Improvements

- SMS-based AQI alerts for users without reliable smartphone/data access
- Multilingual support (Urdu)
- Push notifications when air quality crosses a dangerous threshold for a saved profile
- School/workplace group dashboards for outdoor activity planning
- Expand the advisory engine's rule set with input from actual public health professionals
- Persistent user accounts (currently profiles are created fresh each session)

---

## Team

Built solo in 5 days for the Girls in STEM Global Hackathon.
## API Endpoints

### `GET /api/aqi?city={city_name}`
Returns live AQI data for any city worldwide (geocoded dynamically).

**Example:** `GET /api/aqi?city=Lahore`

**Response (200):**
```json
{
  "aqi_us": 187,
  "category": "Unhealthy",
  "pm25": 62.4,
  "pm10": 95.1,
  "no2": 18.3,
  "so2": 8.7,
  "co": 450.5,
  "o3": 45.2,
  "timestamp": "2026-08-01T05:16:19+00:00",
  "city": "Lahore",
  "country": "PK"
}
```
**Errors:** `400` missing city · `404` city not found · `502` upstream API failure

---

### `POST /api/advisory`
Returns a personalized health advisory given an AQI category and health conditions.

**Body:**
```json
{
  "aqi_category": "Unhealthy",
  "health_conditions": ["asthma", "elderly"]
}
```

**Response (200):**
```json
{
  "aqi_category": "Unhealthy",
  "risk_score": 4,
  "advisories": [
    { "condition": "asthma", "advice": "..." },
    { "condition": "elderly", "advice": "..." }
  ]
}
```

---

### `POST /api/users`
Creates a health profile.

**Body:**
```json
{
  "name": "Aisha",
  "age_group": "adult",
  "health_conditions": ["asthma"],
  "city": "Lahore"
}
```
**Response (201):** `{ "id": 1, "message": "User profile created", "resolved_city": "Lahore" }`

---

### `GET /api/users/{id}/advisory`
**Hero endpoint** — combines a saved profile with live AQI in one call.

**Response (200):**
```json
{
  "user": { "name": "Aisha", "city": "Lahore", "health_conditions": ["asthma"] },
  "current_aqi": { "aqi_us": 187, "category": "Unhealthy", ... },
  "advisory": { "risk_score": 4, "advisories": [...] }
}
```

---

### `GET /api/forecast?city={city_name}`
Pandas-based trend analysis over historical AQI data.

**Response while data is still accumulating (200):**
```json
{
  "status": "insufficient_data",
  "message": "Still collecting historical data for Lahore...",
  "data_points": 2
}
```

**Response once enough data exists (200):**
```json
{
  "status": "ok",
  "trend_direction": "rising",
  "recent_avg_aqi": 172.3,
  "worst_hour_of_day": 8,
  "best_hour_of_day": 14,
  "current_aqi": 187,
  "estimated_next_24h_aqi": 191
}
```

---

## Architecture Notes

- **Local SQLite** (`database/database.py`): stores user health profiles only.
- **Supabase (Postgres)**: stores `aqi_history` and `tracked_cities` — chosen so historical data keeps accumulating 24/7 via a scheduled job, independent of whether the local dev server is running.
- **GitHub Actions** (`.github/workflows/collect_aqi.yml`): runs `scripts/collect_hourly.py` every hour, fetching live AQI for all tracked cities and logging it to Supabase — this is what powers the forecast feature with real, not simulated, historical data.
- Cities are **not hardcoded** — any city a user queries via `/api/aqi` or signs up with is automatically added to `tracked_cities` and starts accumulating history from that point forward.