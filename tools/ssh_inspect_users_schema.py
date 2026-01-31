import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Users Table Info:")
    for row in cursor.execute("PRAGMA table_info(users)"):
        print(row)
        
    conn.close()

if __name__ == "__main__":
    main()
