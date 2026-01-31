import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_super_user():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check user
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username='__super__'")
        user = cursor.fetchone()
        if user:
            print(f"User found: ID={user[0]}, Username={user[1]}")
            print(f"Hash: {user[2][:20]}...")
        else:
            print("User '__super__' NOT found.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_super_user()
