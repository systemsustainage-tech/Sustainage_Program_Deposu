import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def list_tables():
    if not os.path.exists(DB_PATH):
        print("DB not found")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables:")
    for t in tables:
        print(f"- {t[0]}")
        
    # Check specific tables details
    for target in ['eu_taxonomy_data', 'csrd_records', 'audit_logs']:
        print(f"\nSchema for {target}:")
        cursor.execute(f"PRAGMA table_info({target})")
        cols = cursor.fetchall()
        for c in cols:
            print(c)

    conn.close()

if __name__ == "__main__":
    list_tables()
