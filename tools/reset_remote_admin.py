import sqlite3
import os
import sys
from argon2 import PasswordHasher

# Define the correct database path for the remote server
DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

USERNAME = "super.admin"
NEW_PASSWORD = "SuperPassword123!"

def reset_super_admin():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)
        
    print(f"Connecting to database at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id, password_hash, is_active, failed_attempts, locked_until FROM users WHERE username = ?", (USERNAME,))
        user = cursor.fetchone()
        
        ph = PasswordHasher()
        hashed_password = ph.hash(NEW_PASSWORD)
        
        if user:
            print(f"User '{USERNAME}' found. ID: {user[0]}")
            print(f"Status: Active={user[2]}, FailedAttempts={user[3]}, LockedUntil={user[4]}")
            
            # Reset password and lockout status
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, failed_attempts = 0, locked_until = NULL, is_active = 1 
                WHERE username = ?
            """, (hashed_password, USERNAME))
            print(f"Password reset for '{USERNAME}' and account unlocked.")
        else:
            print(f"User '{USERNAME}' not found. Creating...")
            # Create user (assuming company_id=1 for super admin)
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, role, company_id, is_active)
                VALUES (?, ?, 'super.admin@sustainage.com', '__super__', 1, 1)
            """, (USERNAME, hashed_password))
            print(f"User '{USERNAME}' created.")
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error managing user: {e}")
        return False

if __name__ == "__main__":
    if reset_super_admin():
        sys.exit(0)
    else:
        sys.exit(1)
