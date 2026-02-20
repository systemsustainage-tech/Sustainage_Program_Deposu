import sqlite3
import hashlib

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def create_test_user():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Creating users table...")
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    password TEXT,
                    name TEXT,
                    role TEXT,
                    company_id INTEGER
                )
            ''')
            
        # Check if test user exists
        email = 'test@sustainage.com'
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"Test user {email} already exists (ID: {user[0]})")
            # Reset password to '123456' (SHA-256 hash)
            password_hash = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
            cursor.execute("UPDATE users SET password_hash=?, is_active=1, is_verified=1 WHERE id=?", (password_hash, user[0]))
            conn.commit()
            print("Password reset to '123456' (SHA-256 hashed).")
        else:
            print(f"Creating test user {email}...")
            password_hash = '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, is_active, is_verified) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('test_user', email, password_hash, 'Test', 'User', 1, 1))
            conn.commit()
            print("Test user created.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        # Try inspecting columns if failed
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns: {columns}")
        except: pass

if __name__ == "__main__":
    create_test_user()
