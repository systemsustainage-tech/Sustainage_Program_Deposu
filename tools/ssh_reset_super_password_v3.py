import sqlite3
import os
import sys

# Try to import argon2
try:
    from argon2 import PasswordHasher
    PH = PasswordHasher()
    print("Argon2 imported successfully.")
except ImportError:
    print("Argon2 NOT found. Falling back to simple SHA256.")
    import hashlib
    PH = None

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def hash_pass(plain):
    if PH:
        return PH.hash(plain)
    else:
        return hashlib.sha256(plain.encode()).hexdigest()

def main():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    username = '__super__'
    password = 'super123'
    
    # 1. Check if user exists
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    if not row:
        print(f"User {username} not found! Creating...")
        new_hash = hash_pass(password)
        # Using first_name, last_name instead of display_name
        cursor.execute("""
            INSERT INTO users (username, password_hash, first_name, last_name, email, is_active) 
            VALUES (?, ?, ?, ?, ?, 1)
        """, (username, new_hash, 'Super', 'Admin', 'super@sustainage.cloud'))
        user_id = cursor.lastrowid
        print(f"Created user {username} with ID {user_id}")
    else:
        print(f"User {username} found (ID: {row[0]}). Updating password...")
        new_hash = hash_pass(password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, row[0]))
        user_id = row[0]
        
    # 2. Ensure Role
    # Check for Super Admin role
    cursor.execute("SELECT id FROM roles WHERE name = 'super_admin'")
    role_row = cursor.fetchone()
    if not role_row:
        print("Creating super_admin role...")
        cursor.execute("INSERT INTO roles (name, description) VALUES ('super_admin', 'Full Access')")
        role_id = cursor.lastrowid
    else:
        role_id = role_row[0]
        
    # Assign role
    cursor.execute("SELECT 1 FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
    if not cursor.fetchone():
        print(f"Assigning role {role_id} to user {user_id}")
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
        
    conn.commit()
    print(f"Password updated for {username}. New hash start: {new_hash[:20]}...")
    
    # 3. Verify
    if PH:
        try:
            PH.verify(new_hash, password)
            print("Verification Check: SUCCESS")
        except Exception as e:
            print(f"Verification Check: FAILED ({e})")
            
    conn.close()

if __name__ == "__main__":
    main()
