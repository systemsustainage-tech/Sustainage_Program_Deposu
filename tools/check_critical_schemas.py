import sqlite3
import os

DB_PATH = 'sustainage.db'

def check():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tables = ['users', 'energy_consumption', 'water_consumption', 'waste_records']
    
    for t in tables:
        try:
            cursor.execute(f"PRAGMA table_info({t})")
            cols = [c[1] for c in cursor.fetchall()]
            # print(f"{t}: {cols}")
            if 'company_id' in cols:
                print(f"  -> OK: {t} has company_id")
            else:
                print(f"  -> MISSING: {t} missing company_id")
        except Exception as e:
            print(f"Error checking {t}: {e}")
            
    conn.close()

if __name__ == '__main__':
    check()
