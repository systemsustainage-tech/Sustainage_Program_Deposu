import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_schema_and_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("\n--- Schema for waste_generation ---")
        cursor.execute("PRAGMA table_info(waste_generation)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
            
        print("\n--- Data in waste_generation (Last 5) ---")
        cursor.execute("SELECT * FROM waste_generation ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        if not rows:
            print("No data found.")
        else:
            for row in rows:
                print(row)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema_and_data()
