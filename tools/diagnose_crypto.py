
import sys
import os
import sqlite3

# Add backend path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    print("Argon2 imported successfully")
except ImportError as e:
    print(f"Argon2 import failed: {e}")
    sys.exit(1)

from config.database import DB_PATH

def diagnose():
    print(f"DB Path: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT password_hash FROM users WHERE username='admin'").fetchone()
    conn.close()
    
    if not row:
        print("Admin user not found")
        return
        
    stored_hash = row[0]
    print(f"Stored hash: {stored_hash}")
    
    password = "Admin_2025!"
    print(f"Testing password: {password}")
    
    ph = PasswordHasher()
    try:
        ph.verify(stored_hash, password)
        print("VERIFICATION SUCCESSFUL!")
    except VerifyMismatchError:
        print("VERIFICATION FAILED: Mismatch")
    except Exception as e:
        print(f"VERIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose()
