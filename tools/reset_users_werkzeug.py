
import sys
import os
import sqlite3
from werkzeug.security import generate_password_hash

# Add backend path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from config.database import DB_PATH

def reset_users():
    print(f"Connecting to {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Ensure Roles Exist
    roles = ['Admin', 'User', 'Editor', 'Viewer']
    role_ids = {}
    for r in roles:
        cursor.execute("SELECT id FROM roles WHERE name=?", (r,))
        row = cursor.fetchone()
        if row:
            role_ids[r] = row[0]
        else:
            # Need display_name too
            cursor.execute("INSERT INTO roles (name, display_name, description) VALUES (?, ?, ?)", (r, r, f"{r} role"))
            role_ids[r] = cursor.lastrowid
            print(f"Created role: {r}")

    # 2. Reset Users
    users_to_reset = [
        ('admin', 'Admin_2025!', 'Admin'),
        ('test_user', 'Test1234!', 'User')
    ]
    
    for username, password, role_name in users_to_reset:
        print(f"Resetting {username}...")
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        
        # Use werkzeug hash
        pwd_hash = generate_password_hash(password)
        
        if row:
            user_id = row[0]
            cursor.execute("UPDATE users SET password_hash=?, is_active=1 WHERE username=?", (pwd_hash, username))
            print(f"Updated password for {username}.")
        else:
            # Create if not exists
            # Only use columns that we know exist
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (username, f'{username}@example.com', pwd_hash, username.capitalize(), 'User'))
            user_id = cursor.lastrowid
            print(f"Created user {username}.")

        # 3. Assign Role
        target_role_id = role_ids.get(role_name)
        if target_role_id:
            # Check existing role
            cursor.execute("SELECT * FROM user_roles WHERE user_id=? AND role_id=?", (user_id, target_role_id))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, target_role_id))
                print(f"Assigned {role_name} role to {username}.")
            
    conn.commit()
    conn.close()
    print("Reset complete.")

if __name__ == "__main__":
    reset_users()
