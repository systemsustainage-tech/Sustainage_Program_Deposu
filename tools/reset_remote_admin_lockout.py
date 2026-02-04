import os
import sys
import sqlite3
import datetime
import time

# Add project root to path
sys.path.append('/var/www/sustainage')
if os.path.exists('c:/SUSTAINAGESERVER'):
    sys.path.append('c:/SUSTAINAGESERVER')

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
if os.path.exists('c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'):
    DB_PATH = 'c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'

def get_hasher():
    try:
        from backend.security.core.secure_password import hash_password
        return hash_password
    except ImportError:
        try:
            from argon2 import PasswordHasher
            ph = PasswordHasher()
            def hasher(password):
                return f"argon2${ph.hash(password)}"
            return hasher
        except ImportError:
            print("Argon2 not installed.")
            return None

def reset_admin_lockout():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find Super Admin user by username 'admin'
    cursor.execute("""
        SELECT id, username, failed_attempts, locked_until 
        FROM users 
        WHERE username = 'admin'
    """)
    users = cursor.fetchall()

    if not users:
        print("User 'admin' not found.")
        conn.close()
        return

    hasher = get_hasher()
    if not hasher:
        print("Cannot hash password. Aborting.")
        conn.close()
        return

    new_password = "Admin123!"
    password_hash = hasher(new_password)

    for user in users:
        user_id, username, failed, locked = user
        print(f"Found user: {username} (ID: {user_id}) - Failed: {failed}, Locked: {locked}")

        try:
            # Reset lockout and password
            # Schema uses 'password_hash' instead of 'password'
            cursor.execute("""
                UPDATE users 
                SET failed_attempts = 0, 
                    locked_until = NULL,
                    password_hash = ?,
                    must_change_password = 0
                WHERE id = ?
            """, (password_hash, user_id))
            
            if cursor.rowcount > 0:
                print(f"Successfully reset user '{username}'.")
                print(f"  - Password set to: {new_password}")
                print(f"  - Lockout cleared.")
            else:
                print(f"Failed to update user '{username}'.")

        except Exception as e:
            print(f"Error updating user '{username}': {e}")

    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    reset_admin_lockout()
