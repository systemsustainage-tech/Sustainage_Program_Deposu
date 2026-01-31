import sys
import os
import sqlite3

# Add project root to path
sys.path.append('/var/www/sustainage')

try:
    from yonetim.security.core import secure_password
except ImportError:
    print("Could not import yonetim.security.core. Trying direct argon2...")
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        def secure_password(p): return ph.hash(p)
    except ImportError:
        print("Could not import argon2. Exiting.")
        sys.exit(1)

# Correct DB path based on diagnostics
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def reset_password():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    username = '__super__'
    password = 'Kayra_1507'
    
    print(f"Generating hash for {username}...")
    hashed = secure_password(password)
    
    if hashed.startswith('argon2$'):
        final_hash = hashed.replace('argon2$', '')
    else:
        final_hash = hashed
        
    print(f"Hash (preview): {final_hash[:20]}...")

    print(f"Updating password for {username}...")
    # Using 'password_hash' column
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (final_hash, username))
    
    if cursor.rowcount == 0:
        print("User not found!")
    else:
        print("Password updated successfully.")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    reset_password()
