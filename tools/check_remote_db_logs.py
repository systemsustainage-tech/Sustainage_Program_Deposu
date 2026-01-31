
import sqlite3
import sys
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        # Try alternate path
        if os.path.exists('/var/www/sustainage/instance/sustainage.db'):
            print("Found at instance/sustainage.db instead.")
            return
        return

    print(f"Checking DB at {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found: {len(tables)}")
        
        if 'system_logs' in tables:
            print("system_logs table exists.")
            cursor.execute("PRAGMA table_info(system_logs);")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("system_logs table MISSING.")
            
        conn.close()
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == '__main__':
    check_db()
