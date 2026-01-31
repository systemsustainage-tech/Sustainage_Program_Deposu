import sqlite3
import os

# Correct DB Path based on remote_web_app.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    print(f"Migrating DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tables = ['users', 'energy_consumption', 'water_consumption', 'waste_records']
    
    for t in tables:
        try:
            # Check if table exists first
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{t}'")
            if not cursor.fetchone():
                print(f"Skipping {t}: Table does not exist!")
                continue

            # Check if column exists
            cursor.execute(f"PRAGMA table_info({t})")
            cols = [c[1] for c in cursor.fetchall()]
            
            if 'company_id' in cols:
                print(f"Skipping {t}: already has company_id")
            else:
                print(f"Adding company_id to {t}...")
                cursor.execute(f"ALTER TABLE {t} ADD COLUMN company_id INTEGER DEFAULT 1")
                conn.commit()
                print(f"  -> Done.")
                
        except Exception as e:
            print(f"Error migrating {t}: {e}")
            
    conn.close()

if __name__ == '__main__':
    migrate()
