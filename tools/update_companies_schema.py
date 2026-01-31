import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check companies table columns
    cur.execute("PRAGMA table_info(companies)")
    columns = [info[1] for info in cur.fetchall()]
    
    print(f"Current columns in companies: {columns}")
    
    if 'country' not in columns:
        print("Adding country column...")
        try:
            cur.execute("ALTER TABLE companies ADD COLUMN country TEXT")
        except Exception as e:
            print(f"Error adding country: {e}")

    if 'tax_number' not in columns:
        print("Adding tax_number column...")
        try:
            cur.execute("ALTER TABLE companies ADD COLUMN tax_number TEXT")
        except Exception as e:
            print(f"Error adding tax_number: {e}")

    if 'is_active' not in columns:
        print("Adding is_active column...")
        try:
            cur.execute("ALTER TABLE companies ADD COLUMN is_active BOOLEAN DEFAULT 1")
        except Exception as e:
            print(f"Error adding is_active: {e}")
            
    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    fix_schema()
