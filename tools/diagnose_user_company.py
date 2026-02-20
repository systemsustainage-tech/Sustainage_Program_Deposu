import sqlite3
import sys
import os

# Cross-platform DB Path
if os.name == 'nt':
    DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
else:
    DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

def diagnose_user(username):
    print(f"Diagnosing user: {username}")
    print(f"Using DB: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB File does not exist!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Check user exists
    try:
        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    except sqlite3.OperationalError as e:
        print(f"Error querying users table: {e}")
        # List all tables
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print("Tables available:", [t['name'] for t in tables])
        return

    if not user:
        print("User NOT FOUND in 'users' table.")
        # Check if any users exist
        count = cursor.execute("SELECT count(*) FROM users").fetchone()[0]
        print(f"Total users in DB: {count}")
        return
    
    print(f"User found: ID={user['id']}, Username={user['username']}")
    
    # 2. Check user_companies
    print("\nChecking 'user_companies' table:")
    companies = cursor.execute("SELECT * FROM user_companies WHERE user_id = ?", (user['id'],)).fetchall()
    if not companies:
        print("NO ENTRIES in 'user_companies' for this user.")
    else:
        for c in companies:
            print(f"  - company_id: {c['company_id']}, is_primary: {c['is_primary']}")

    # 3. Check companies table
    print("\nChecking 'companies' table:")
    all_companies = cursor.execute("SELECT id, name FROM companies").fetchall()
    for c in all_companies:
        print(f"  - ID: {c['id']}, Name: {c['name']}")

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = "super.admin"
    
    diagnose_user(username)
