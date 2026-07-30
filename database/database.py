import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "aawazair.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_connection():
    """Returns a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns like a dict: row["name"]
    return conn


def init_db():
    """Creates tables from schema.sql if they don't already exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = get_connection()
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized.")


def insert_user(name, age_group, health_conditions, city):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, age_group, health_conditions, city) VALUES (?, ?, ?, ?)",
        (name, age_group, health_conditions, city)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def insert_aqi_reading(city, aqi_us, category, pm25, pm10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO aqi_history (city, aqi_us, category, pm25, pm10) VALUES (?, ?, ?, ?, ?)",
        (city, aqi_us, category, pm25, pm10)
    )
    conn.commit()
    conn.close()


def get_aqi_history(city, limit=168):
    """Returns recent AQI readings for a city, most recent first. Default limit = 7 days of hourly data."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM aqi_history WHERE city = ? ORDER BY recorded_at DESC LIMIT ?",
        (city, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]



init_db()
uid = insert_user("Test User", "adult", "asthma", "Lahore")
print("Inserted user ID:", uid)
print(get_user(uid))

insert_aqi_reading("Lahore", 187, "Unhealthy", 62.4, 95.1)
print(get_aqi_history("Lahore"))