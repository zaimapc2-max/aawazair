import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "aawazair.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_connection():
    """Returns a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the local users table if it doesn't already exist."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = get_connection()
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Local database initialized.")


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