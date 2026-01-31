import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check():
    print(f"Checking DB at {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables_to_check = ['training_materials', 'stakeholder_training_progress', 'stakeholders']
    for table in tables_to_check:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            print(f"[OK] Table {table} exists.")
            # Check columns for stakeholders
            if table == 'stakeholders':
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [c[1] for c in cursor.fetchall()]
                required = ['portal_access_token', 'portal_enabled', 'last_contacted']
                for req in required:
                    if req in cols:
                        print(f"  [OK] Column {req} exists.")
                    else:
                        print(f"  [FAIL] Column {req} MISSING.")
        else:
            print(f"[FAIL] Table {table} MISSING.")
            
    conn.close()

if __name__ == "__main__":
    check()
