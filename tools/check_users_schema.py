import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Checking 'users' table schema:")
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
        
    conn.close()

if __name__ == '__main__':
    check_schema()
