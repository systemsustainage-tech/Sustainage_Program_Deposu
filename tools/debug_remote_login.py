import sqlite3
import os
import sys

# Setup paths
sys.path.append('/var/www/sustainage')
if os.path.exists('c:/SUSTAINAGESERVER'):
    sys.path.append('c:/SUSTAINAGESERVER')

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
if os.path.exists('c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'):
    DB_PATH = 'c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'

def test_login(username, password):
    print(f"--- Testing Login for '{username}' ---")
    
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Fetch User
    cursor.execute("SELECT id, password_hash, is_active, failed_attempts, locked_until FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        print("User not found.")
        conn.close()
        return

    user_id, stored_hash, is_active, failed, locked = user
    print(f"User ID: {user_id}")
    print(f"Is Active: {is_active}")
    print(f"Failed Attempts: {failed}")
    print(f"Locked Until: {locked}")
    print(f"Stored Hash: {stored_hash}")

    conn.close()

    # 2. Verify Password
    try:
        from backend.security.core.secure_password import verify_password
        print("Imported verify_password from backend.")
        
        is_valid, needs_rehash = verify_password(stored_hash, password)
        print(f"Verification Result: {is_valid}")
        print(f"Needs Rehash: {needs_rehash}")
        
        if is_valid:
            print("SUCCESS: Password is correct.")
        else:
            print("FAILURE: Password verification failed.")
            
    except ImportError as e:
        print(f"Import Error: {e}")
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login("admin", "Admin123!")
