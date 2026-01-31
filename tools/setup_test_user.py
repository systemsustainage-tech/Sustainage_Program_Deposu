import sqlite3
from argon2 import PasswordHasher
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def create_test_user():
    """Creates a test user if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    username = "test_user"
    password = "Test1234!"
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        ph = PasswordHasher()
        password_hash = ph.hash(password)
        
        if user:
            logging.info(f"User {username} exists. Updating password...")
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
        else:
            logging.info(f"Creating user {username}...")
            cursor.execute("""
                INSERT INTO users (username, password_hash, is_active, first_name, last_name, email)
                VALUES (?, ?, 1, 'Test', 'User', 'test@sustainage.cloud')
            """, (username, password_hash))
            
        conn.commit()
        logging.info("Test user setup complete.")
        
    except Exception as e:
        logging.error(f"Error setting up test user: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_user()
