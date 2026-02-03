import os
import sys
import sqlite3
import datetime

# Add project root to path to import backend modules
sys.path.append('/var/www/sustainage')

try:
    from backend.security.core.secure_password import hash_password
    print("Successfully imported hash_password from backend.")
except ImportError as e:
    print(f"Could not import hash_password: {e}")
    print("Falling back to local implementation or standard generation.")
    # Fallback if module not found, though it should be there
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        def hash_password(password):
            return f"argon2${ph.hash(password)}"
    except ImportError:
        print("Argon2 not installed. Please install argon2-cffi.")
        sys.exit(1)

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def create_admin():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    username = "admin"
    email = "admin@sustainage.com"
    # Default password: Admin123!
    password_plain = "Admin123!"
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"User '{username}' already exists.")
        conn.close()
        return

    print(f"Creating user '{username}'...")
    
    try:
        password_hash = hash_password(password_plain)
        
        # Ensure company 1 exists (we did this in init_remote_data.py, but safe to check)
        cursor.execute("SELECT id FROM companies WHERE id = 1")
        if not cursor.fetchone():
            print("Company ID 1 not found. Creating default company...")
            cursor.execute("INSERT INTO companies (id, name, sector, employee_count) VALUES (1, 'Sustainage HQ', 'Tech', 10)")
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO users (
                username, password, email, role, company_id, is_active, 
                created_at, failed_attempts, must_change_password
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, 
            password_hash, 
            email, 
            'super_admin', 
            1, 
            1, 
            now, 
            0, 
            1  # Force password change on first login for security
        ))
        
        conn.commit()
        print(f"Super Admin created successfully.")
        print(f"Username: {username}")
        print(f"Password: {password_plain}")
        print("NOTE: 'must_change_password' is set to 1.")
        
    except Exception as e:
        print(f"Error creating user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin()
