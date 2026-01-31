import sqlite3
import os
import sys

# Add backend to path to import hashing functions
sys.path.append('/var/www/sustainage')
from backend.yonetim.security.core.crypto import hash_password

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def reset_super_user():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    username = '__super__'
    new_password = 'Kayra_1507'
    
    # Check schema
    print("--- Users Table Schema ---")
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    print(columns)
    
    # 1. Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    
    pw_hash = hash_password(new_password)
    
    if not row:
        print(f"User {username} not found. Creating...")
        # Construct INSERT based on available columns
        fields = ["username", "password_hash", "role", "is_active", "display_name"]
        valid_fields = [f for f in fields if f in columns]
        placeholders = ",".join(["?"] * len(valid_fields))
        query = f"INSERT INTO users ({','.join(valid_fields)}) VALUES ({placeholders})"
        
        values = []
        for f in valid_fields:
            if f == "username": values.append(username)
            elif f == "password_hash": values.append(pw_hash)
            elif f == "role": values.append("super_admin")
            elif f == "is_active": values.append(1)
            elif f == "display_name": values.append("Super Admin")
            
        cursor.execute(query, values)
        print("User created.")
    else:
        print(f"User {username} found. ID: {row[0]}")
        # Construct UPDATE based on available columns
        updates = ["password_hash = ?", "is_active = ?"]
        values = [pw_hash, 1]
        
        if "failed_login_attempts" in columns:
            updates.append("failed_login_attempts = ?")
            values.append(0)
        if "failed_attempts" in columns:
            updates.append("failed_attempts = ?")
            values.append(0)
        if "lockout_until" in columns:
            updates.append("lockout_until = ?")
            values.append(None)
        if "locked_until" in columns:
            updates.append("locked_until = ?")
            values.append(None)
            
        values.append(username)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
        cursor.execute(query, values)
        print(f"Password updated using columns: {', '.join(updates)}")

    conn.commit()
    conn.close()
    print(f"Password for {username} set to: {new_password}")

if __name__ == "__main__":
    try:
        reset_super_user()
    except Exception as e:
        print(f"Critical error: {e}")
