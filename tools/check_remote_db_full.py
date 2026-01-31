import os
import sqlite3

POSSIBLE_PATHS = [
    '/var/www/sustainage/backend/data/sdg_desktop.sqlite',
    '/var/www/sustainage/sustainage.db'
]

def list_tables():
    db_path = None
    for p in POSSIBLE_PATHS:
        if os.path.exists(p):
            db_path = p
            print(f"Found DB at: {p}")
            break
            
    if not db_path:
        print("No database found!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in {db_path}:")
        count = 0
        for t in tables:
            print(f"- {t[0]}")
            count += 1
        print(f"Total tables: {count}")
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if cursor.fetchone():
            print("Users table FOUND.")
            # Check __super__
            try:
                cursor.execute("SELECT username, password FROM users WHERE username='__super__'")
                user = cursor.fetchone()
                if user:
                    print(f"__super__ found. Hash start: {user[1][:10]}...")
                else:
                    print("__super__ NOT found.")
            except Exception as e:
                print(f"Error querying users: {e}")
        else:
            print("Users table NOT found.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    list_tables()
