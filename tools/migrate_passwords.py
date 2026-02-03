import sqlite3
import os
import sys
import hashlib
import time

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from yonetim.security.core.crypto import hash_password as argon2_hash
except ImportError:
    print("Error: Could not import yonetim.security.core.crypto. Make sure you are in the project root or tools directory.")
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        argon2_hash = ph.hash
    except ImportError:
        print("Critical Error: argon2-cffi not installed. Run 'pip install argon2-cffi'.")
        sys.exit(1)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'sdg_desktop.sqlite')
# If running on remote linux
if not os.path.exists(DB_PATH) and os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def migrate_passwords():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Opening database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all users
    try:
        cursor.execute("SELECT id, username, password_hash FROM users")
        users = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Error reading users table: {e}")
        conn.close()
        return

    migrated_count = 0
    skipped_count = 0
    
    print(f"Found {len(users)} users. Checking for SHA-256 hashes...")
    
    for user_id, username, password_hash in users:
        if not password_hash:
            continue
            
        # Check if it looks like a raw SHA-256 hash
        # Length 64, hex characters only, no prefixes
        is_sha256 = False
        if len(password_hash) == 64:
            try:
                int(password_hash, 16)
                is_sha256 = True
            except ValueError:
                pass
        
        if is_sha256:
            print(f"Migrating user '{username}' (ID: {user_id})...")
            
            # Strategy: Hash the existing SHA-256 hash with Argon2
            # New format: argon2_sha256$<argon2_hash_of_sha256_hash>
            
            # 1. Hash the SHA-256 string with Argon2
            new_inner_hash = argon2_hash(password_hash)
            
            # 2. Add our custom prefix
            final_hash = f"argon2_sha256${new_inner_hash}"
            
            # 3. Update DB
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (final_hash, user_id))
            migrated_count += 1
        else:
            # Already migrated or using another format (e.g. pbkdf2, or standard argon2)
            skipped_count += 1
            # Optional: Upgrade PBKDF2? 
            # If we wanted to upgrade PBKDF2, we'd need to do the same double-hashing, 
            # but user specifically asked for SHA-256 to Argon2.
            
    conn.commit()
    conn.close()
    
    print("-" * 30)
    print(f"Migration Complete.")
    print(f"Migrated: {migrated_count}")
    print(f"Skipped:  {skipped_count}")

if __name__ == "__main__":
    migrate_passwords()
