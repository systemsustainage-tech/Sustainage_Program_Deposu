
import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def create_admin():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        username = "super.admin"
        password = "SuperPassword123!"
        email = "super.admin@sustainage.app"
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        password_hash = generate_password_hash(password)
        
        if user:
            print(f"User {username} exists (ID: {user['id']}). Updating password...")
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, failed_attempts = 0, locked_until = NULL, is_active = 1
                WHERE id = ?
            """, (password_hash, user['id']))
        else:
            print(f"User {username} does not exist. Creating...")
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, is_active, is_verified)
                VALUES (?, ?, ?, 'Super', 'Admin', 1, 1)
            """, (username, email, password_hash))
            user_id = cursor.lastrowid
            print(f"User created with ID: {user_id}")
            
            # Ensure company exists
            cursor.execute("SELECT id FROM companies LIMIT 1")
            company = cursor.fetchone()
            if not company:
                print("No company found. Creating Default Company...")
                cursor.execute("INSERT INTO companies (name) VALUES ('Default Company')")
                company_id = cursor.lastrowid
            else:
                company_id = company['id']
            
            # Assign to company
            cursor.execute("INSERT OR IGNORE INTO user_companies (user_id, company_id, is_primary) VALUES (?, ?, 1)", (user_id, company_id))
            print(f"Assigned to Company ID: {company_id}")

        conn.commit()
        conn.close()
        print("Done.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_admin()
