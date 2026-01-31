import sqlite3
import os

DB_PATH = os.path.join('backend', 'data', 'sdg_desktop.sqlite')

def check_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Listing all tables in {DB_PATH}...")
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    for t in tables:
        print(f"- {t[0]}")
            
    conn.close()

if __name__ == "__main__":
    check_tables()
