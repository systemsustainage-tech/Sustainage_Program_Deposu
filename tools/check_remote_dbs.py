import sqlite3
import os
import sys

# Define paths to check
PATHS = [
    '/var/www/sustainage/backend/data/sdg_prod.sqlite',
    '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
]

def check_db(path):
    print(f"\n--- Checking {path} ---")
    if not os.path.exists(path):
        print("FILE DOES NOT EXIST")
        return

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Check users table
        try:
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print(f"Columns in users table: {[c[1] for c in columns]}")

            # Try to guess password column
            pwd_col = 'password'
            if 'password_hash' in [c[1] for c in columns]:
                pwd_col = 'password_hash'
            
            cursor.execute(f"SELECT id, username, {pwd_col}, company_id FROM users WHERE username = 'super.admin'")
            user = cursor.fetchone()
            if user:
                print(f"FOUND super.admin: ID={user[0]}, CompanyID={user[3]}")
                print(f"Password Hash prefix: {user[2][:20]}...")
            else:
                print("super.admin NOT FOUND in users table")
                
                # List all users
                cursor.execute("SELECT username FROM users LIMIT 5")
                users = cursor.fetchall()
                print(f"First 5 users: {[u[0] for u in users]}")
                
        except sqlite3.OperationalError as e:
            print(f"Error querying users table: {e}")
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                print("Table 'users' DOES NOT EXIST")

        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    for path in PATHS:
        check_db(path)
