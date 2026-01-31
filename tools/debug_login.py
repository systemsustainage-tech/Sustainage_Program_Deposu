
import sqlite3
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.yonetim.security.core.crypto import verify_password_compat, hash_password

def check_login(username, password):
    db_path = 'backend/data/sdg_desktop.sqlite'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Checking user: {username}")
    cursor.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("User not found!")
        return
        
    user_id, stored_hash = row
    print(f"User found. ID: {user_id}")
    print(f"Stored Hash: {stored_hash}")
    
    is_valid = verify_password_compat(stored_hash, password)
    print(f"Password '{password}' valid? : {is_valid}")
    
    # Try re-hashing to see what it generates
    new_hash = hash_password(password)
    print(f"New Hash generated for '{password}': {new_hash}")

if __name__ == "__main__":
    check_login('admin', 'admin123') # Assuming default password might be admin123 or similar
    check_login('admin', 'admin')
    check_login('test_user', 'password')
