import sqlite3
import hashlib
import secrets
import os

DB_PATH = '/var/www/sustainage/sustainage.db'

def hash_password(password):
    # Use simple SHA256 for compatibility with verify_password_compat
    # This avoids potential salt prefix mismatches with PBKDF2
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_user():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        username = 'test_user'
        password = 'Test1234!'
        email = 'test_user@sustainage.com'
        
        # Check if exists
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        
        if row:
            print(f"User {username} already exists (ID: {row[0]}). Updating password...")
            user_id = row[0]
            pw_hash = hash_password(password)
            cur.execute("UPDATE users SET password_hash = ?, is_active = 1 WHERE id = ?", (pw_hash, user_id))
        else:
            print(f"Creating user {username}...")
            pw_hash = hash_password(password)
            cur.execute("""
                INSERT INTO users (username, password_hash, email, is_active, first_name, last_name)
                VALUES (?, ?, ?, 1, 'Test', 'User')
            """, (username, pw_hash, email))
            user_id = cur.lastrowid
            print(f"Created user {username} with ID {user_id}")
            
        # Assign Role
        cur.execute("SELECT id FROM roles WHERE name = 'User'")
        role_row = cur.fetchone()
        if not role_row:
            print("Role 'User' not found. Creating...")
            cur.execute("INSERT INTO roles (name, display_name) VALUES ('User', 'Kullanıcı')")
            role_id = cur.lastrowid
        else:
            role_id = role_row[0]
            
        # Check if user has role
        cur.execute("SELECT * FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
        if not cur.fetchone():
            print(f"Assigning role {role_id} to user {user_id}")
            cur.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
        else:
            print("User already has the role.")
            
        conn.commit()
        conn.close()
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_user()
