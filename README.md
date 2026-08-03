# AawazAir

**Personalized Air Quality Health Advisor**

Built for the Girls in STEM Global Hackathon — *Global Challenges, Local Solutions*

🔗 **Live Demo:** https://aawazair-production.up.railway.app
📦 **Repo:** https://github.com/zaimapc2-max/aawazair

---

## The Problem

Lahore and much of Punjab routinely experience "hazardous" air quality during smog season, yet public health messaging stays generic — "wear a mask" tells a healthy adult and someone with asthma the exact same thing, when their actual risk and the right response are completely different. Existing AQI apps show a number. They don't tell a parent whether it's safe to send their child outside today, or tell someone with asthma when to avoid exercise.

AawazAir turns a raw AQI number into a **personalized health advisory** — based on your age group and health conditions, using thresholds grounded in WHO/EPA air quality guidance — plus a live-collected historical trend so you can see how air quality has actually been moving in your city, not just right now.

---

## Screenshots

*(add 2–3 screenshots here — main AQI reading, personalized advisory card, multi-city comparison)*

---

## Features

- **Live AQI** for any city worldwide, calculated using the real EPA PM2.5-to-AQI breakpoint formula (not just a passthrough of a raw API number)
- **Personalized health advisory** — factors in age group (child/elderly) and health conditions (asthma, pregnant), with prioritized, combined advice when multiple conditions apply
- **7-day trend chart** built from real, automatically-collected historical data — not simulated
- **Multi-city comparison** — check several cities side by side
- **Automatic hourly data collection** via GitHub Actions + Supabase, running independently of whether the app itself is being actively used
- **Instrument-panel visual design** — a breathing glow behind the live reading, tinted to match the current AQI category

---

## Tech Stack

- **Backend:** Python, Flask
- **Data analysis:** Pandas (trend/forecast logic)
- **Databases:** SQLite (local health profiles) + Supabase/Postgres (historical AQI data — chosen so data keeps accumulating 24/7 regardless of whether the local server is running)
- **Automation:** GitHub Actions scheduled workflow, running hourly to collect live AQI data
- **Frontend:** HTML, CSS, vanilla JavaScript, Chart.js
- **Hosting:** Railway
- **External API:** OpenWeatherMap (Air Pollution + Geocoding)

---

## Architecture

```
                    ┌─────────────────────┐
                    │  GitHub Actions      │
                    │  (runs every hour)   │
                    └──────────┬───────────┘
                               │
                               ▼
┌──────────────┐      ┌───────────────┐      ┌──────────────────┐
│ OpenWeatherMap│◄────►│  Flask Backend │◄────►│  Supabase (Postgres)│
│  (live AQI +  │      │  (app.py)      │      │  aqi_history,       │
│   geocoding)  │      │  hosted on     │      │  tracked_cities      │
│               │      │  Railway       │      │                      │
└──────────────┘      └───────┬────────┘      └──────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  SQLite (local)      │
                    │  users table only     │
                    └─────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Frontend (HTML/JS)   │
                    │  Chart.js, live badge │
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

- **Supabase Row Level Security** initially blocked reads/writes via the anon key, with no obvious error message — RLS was disabled on `aqi_history` and `tracked_cities` after tracing an empty result back to it, since this data isn't sensitive (no personal user data lives here — health profiles stay in local SQLite).
- **A freshly generated OpenWeatherMap API key can take time to activate** — including on a brand-new account — and looks identical to an invalid key until it does. Worth knowing before assuming a key is broken.
- **`.env` files and CI/CD secrets (e.g. GitHub Actions) are two entirely separate systems** that don't sync automatically — a variable name mismatch between the two caused automated data collection to silently fail for a while.
- Historical data is genuinely, continuously collected in the background via a GitHub Actions cron job — not simulated or seeded — so the trend chart and forecast feature reflect real conditions and get more accurate the longer the system runs.

---

## Future Improvements

- SMS-based AQI alerts for users without reliable smartphone/data access
- Multilingual support (Urdu)
- Push notifications when air quality crosses a dangerous threshold for a saved profile
- School/workplace group dashboards for outdoor activity planning
- Expand the advisory engine's rule set with input from actual public health professionals
- Persistent user accounts (currently profiles are created fresh each session)
- Migrate the Flask dev server to a production WSGI server (e.g. Gunicorn) for a more robust deployment

---

## Team

Built solo in 5 days for the Girls in STEM Global Hackathon.