import sqlite3
import os
import sys

# Define the correct database path for the remote server
DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

def inspect_users_table():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)
        
    print(f"Connecting to database at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check users table info
        print("--- Table Info: users ---")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
            
        # Check first user to see data structure
        print("\n--- First 3 Users ---")
        cursor.execute("SELECT * FROM users LIMIT 3")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            
        conn.close()
        return True
    except Exception as e:
        print(f"Error inspecting database: {e}")
        return False

if __name__ == "__main__":
    if inspect_users_table():
        sys.exit(0)
    else:
        sys.exit(1)
