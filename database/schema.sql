CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age_group TEXT NOT NULL,        -- 'child', 'adult', 'elderly'
    health_conditions TEXT,          -- comma-separated: 'asthma,pregnant' or 'none'
    city TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);