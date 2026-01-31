
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- water_consumption Schema ---")
    cursor.execute("PRAGMA table_info(water_consumption)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
        
    print("\n--- Recent 5 records ---")
    cursor.execute("SELECT * FROM water_consumption ORDER BY created_at DESC LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    check_schema()
