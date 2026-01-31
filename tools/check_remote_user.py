import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import hash verification
try:
    from yonetim.security.core.crypto import verify_password
except ImportError:
    try:
        from backend.yonetim.security.core.crypto import verify_password
    except ImportError:
        verify_password = None

def check_user():
    db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    print(f"Checking user __super__ in {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password_hash, is_active FROM users WHERE username = '__super__'")
    row = cursor.fetchone()
    
    if row:
        print(f"User found: ID={row[0]}, Username={row[1]}, Active={row[3]}")
        print(f"Hash prefix: {row[2][:20]}...")
        
        if verify_password:
            try:
                is_valid = verify_password("Kayra_1507", row[2])
                print(f"Password 'Kayra_1507' verification: {is_valid}")
            except Exception as e:
                print(f"Verification error: {e}")
        else:
            print("Could not import verify_password to test.")
    else:
        print("User __super__ NOT FOUND.")
        
    conn.close()

if __name__ == "__main__":
    check_user()
