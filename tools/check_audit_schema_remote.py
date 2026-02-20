import sqlite3
import os
import sys

# Define path directly to avoid config ambiguity
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_schema():
    print(f"Checking schema for {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database file does not exist!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = cursor.fetchall()
        
        if not columns:
            print("Table audit_logs does not exist.")
        else:
            print("Columns in audit_logs:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
