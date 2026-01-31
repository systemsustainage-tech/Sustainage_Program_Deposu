
import sqlite3

DB_PATH = 'backend/data/sdg_desktop.sqlite'

def check_gri():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("--- Schema for gri_standards ---")
        try:
            cursor.execute("PRAGMA table_info(gri_standards)")
            columns = cursor.fetchall()
            if not columns:
                print("Table gri_standards does not exist.")
            for col in columns:
                print(col)
        except Exception as e:
            print(f"Error: {e}")
            
        print("\n--- Content sample ---")
        try:
            cursor.execute("SELECT * FROM gri_standards LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except:
            pass
            
        conn.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    check_gri()
