import sqlite3
import os
import sys

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    print(f"Fixing schema for {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database file does not exist!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]
        
        print(f"Current columns: {columns}")
        
        if 'details' not in columns:
            print("Adding details column...")
            try:
                cursor.execute("ALTER TABLE audit_logs ADD COLUMN details TEXT")
                print("Added details column.")
            except Exception as e:
                print(f"Error adding details: {e}")
        else:
            print("details column already exists.")

        conn.commit()
        conn.close()
        print("Fix completed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_schema()
