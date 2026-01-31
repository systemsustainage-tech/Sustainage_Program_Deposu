
import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def fix_system_settings():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(system_settings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print("Adding company_id to system_settings...")
            cursor.execute("ALTER TABLE system_settings ADD COLUMN company_id INTEGER DEFAULT 1")
            
            # Update existing records to default company (1)
            cursor.execute("UPDATE system_settings SET company_id = 1 WHERE company_id IS NULL")
            conn.commit()
            print("Successfully added company_id column.")
        else:
            print("system_settings already has company_id.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_system_settings()
