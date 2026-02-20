import sqlite3
import sys
import os

# Add root to sys.path to find backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.security.core.secure_password import hash_password

if os.name == 'nt':
    DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
else:
    DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

def reset_password(username, new_password):
    print(f"Resetting password for {username}...")
    
    hashed = hash_password(new_password)
    print(f"New Hash: {hashed}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed, username))
        if cursor.rowcount > 0:
            print("Password updated successfully.")
            conn.commit()
        else:
            print("User not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        reset_password(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python reset_remote_password.py <username> <password>")
