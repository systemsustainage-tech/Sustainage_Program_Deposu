import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_users():
    try:
        if not os.path.exists(DB_PATH):
            print(f"DB not found at {DB_PATH}")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Users table columns: {columns}")
        
        if 'email' in columns:
            print("Email column exists.")
        else:
            print("Email column MISSING!")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
