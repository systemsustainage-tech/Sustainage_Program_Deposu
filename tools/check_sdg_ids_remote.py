import sqlite3

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_schema_and_ids():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("--- SDG Goals Schema ---")
        cursor.execute("PRAGMA table_info(sdg_goals)")
        columns = [info[1] for info in cursor.fetchall()]
        print(columns)
        
        print("\n--- Data Sample ---")
        # Select all columns
        cursor.execute(f"SELECT * FROM sdg_goals LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema_and_ids()
