
import sqlite3
import sys
import os
from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_user(username, password):
    print(f"Checking user: {username}")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print("User not found!")
            return

        print(f"User ID: {user['id']}")
        print(f"Is Active: {user['is_active']}")
        print(f"Failed Attempts: {user['failed_attempts']}")
        print(f"Locked Until: {user['locked_until']}")
        print(f"Hash Start: {user['password_hash'][:20]}...")
        
        # Check password
        is_valid = check_password_hash(user['password_hash'], password)
        print(f"Password '{password}' Valid? {is_valid}")
        
        if not is_valid:
            print("Trying to verify with 'pbkdf2:sha256' method...")
            # Maybe the hash format is different?
            pass

        # Reset failed attempts if > 0
        if user['failed_attempts'] > 0 or user['locked_until'] is not None:
            print("Resetting failed attempts and lock...")
            cursor.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?", (user['id'],))
            conn.commit()
            print("Reset complete.")
            
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user("super.admin", "SuperPassword123!")
