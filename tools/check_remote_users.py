import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_users():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        print("\n--- Users ---")
        try:
            cur.execute("SELECT id, username, is_active FROM users")
            users = cur.fetchall()
            for user in users:
                print(user)
                
            # Check roles
            print("\n--- User Roles ---")
            cur.execute("""
                SELECT u.username, r.name 
                FROM users u 
                JOIN user_roles ur ON u.id = ur.user_id 
                JOIN roles r ON ur.role_id = r.id
            """)
            roles = cur.fetchall()
            for role in roles:
                print(role)
                
        except Exception as e:
            print(f"Error querying users: {e}")
            
        conn.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    check_users()
