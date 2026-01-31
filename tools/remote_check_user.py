import sqlite3
import sys
import os

# Adjust path to find config
sys.path.append('/var/www/sustainage')

try:
    from config.database import DB_PATH
except ImportError:
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_user(username):
    print(f"Checking user '{username}' in database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        if user:
            print(f"User found: {dict(user)}")
            # Check roles
            roles = cursor.execute("""
                SELECT r.name 
                FROM roles r 
                JOIN user_roles ur ON r.id = ur.role_id 
                WHERE ur.user_id = ?
            """, (user['id'],)).fetchall()
            role_names = [r['name'] for r in roles]
            print(f"Roles: {role_names}")
        else:
            print("User NOT found.")
            
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_user('test_user')
