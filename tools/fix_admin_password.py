
import sqlite3
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.yonetim.security.core.crypto import hash_password

def reset_admin_password():
    db_path = 'backend/data/sdg_desktop.sqlite'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    new_password = 'admin'
    new_hash = hash_password(new_password)
    
    print(f"Resetting admin password to '{new_password}'...")
    print(f"New Hash: {new_hash}")
    
    cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_hash,))
    
    if cursor.rowcount > 0:
        print("Admin password updated successfully.")
        conn.commit()
    else:
        print("Admin user not found!")
        
    conn.close()

if __name__ == "__main__":
    reset_admin_password()
