import os
import sqlite3
import sys

def get_db_path():
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config.database import DB_PATH
        if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
            return '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
        return DB_PATH
    except Exception:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.name == 'nt':
            return os.path.join(base_dir, 'backend', 'data', 'sdg_desktop.sqlite')
        if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
            return '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
        return '/var/www/sustainage/sustainage.db'

def init_surveys(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            response_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            respondent TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (survey_id) REFERENCES surveys(id)
        )
    """)
    conn.commit()
    conn.close()
    print("Surveys schema initialized.")

if __name__ == "__main__":
    db_path = get_db_path()
    print(f"DB_PATH: {db_path}")
    init_surveys(db_path)
