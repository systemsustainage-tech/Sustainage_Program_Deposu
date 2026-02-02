
import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'sustainage.db')

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. List tables
    print("--- TABLES ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for t in tables:
        print(t[0])
        
    # 2. Check online_surveys if exists
    if ('online_surveys',) in tables:
        print("\n--- ONLINE_SURVEYS SCHEMA ---")
        cursor.execute("PRAGMA table_info(online_surveys)")
        columns = cursor.fetchall()
        for c in columns:
            print(c)
            
        print("\n--- ONLINE_SURVEYS DATA (First 5) ---")
        try:
            cursor.execute("SELECT id, survey_link, is_active FROM online_surveys LIMIT 5")
            rows = cursor.fetchall()
            for r in rows:
                print(r)
        except Exception as e:
            print(f"Error reading data: {e}")
    else:
        print("\nTable 'online_surveys' does not exist.")
        
    # 3. Check surveys table if exists (alternative)
    if ('surveys',) in tables:
        print("\n--- SURVEYS SCHEMA ---")
        cursor.execute("PRAGMA table_info(surveys)")
        columns = cursor.fetchall()
        for c in columns:
            print(c)

    conn.close()

if __name__ == "__main__":
    check_db()
