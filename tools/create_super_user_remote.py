import sqlite3
import logging
import os
import sys
from argon2 import PasswordHasher

# Configuration
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    if not os.path.exists(DB_PATH):
        logging.error(f"DB not found at {DB_PATH}")
        return

    ph = PasswordHasher()
    username = "__super__"
    password = "super123"
    hashed_password = ph.hash(password)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logging.info(f"Creating/Updating super user '{username}'...")
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            logging.info(f"User exists (ID: {user_id}). Updating password...")
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
        else:
            logging.info("User does not exist. Creating...")
            cursor.execute("INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)", 
                           (username, hashed_password, 'admin', 1))
            user_id = cursor.lastrowid
            logging.info(f"User created (ID: {user_id}).")

        # Ensure admin role
        logging.info("Ensuring admin role...")
        cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
        role_res = cursor.fetchone()
        if role_res:
            role_id = role_res[0]
            cursor.execute("SELECT * FROM user_roles WHERE user_id = ? AND role_id = ?", (user_id, role_id))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO user_roles (user_id, role_id, assigned_at, assigned_by) VALUES (?, ?, datetime('now'), 'system')", (user_id, role_id))
                logging.info("Admin role assigned.")
        
        conn.commit()
        conn.close()
        logging.info("Super user setup complete.")

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
