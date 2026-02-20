import sqlite3
import sys
import os

if os.name == 'nt':
    DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
else:
    DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

def check_user(username):
    print(f"Checking user: {username}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user:
            print("User found:")
            for key in user.keys():
                val = user[key]
                if key == 'password_hash':
                    val = val[:20] + "..." if val else "None"
                print(f"  {key}: {val}")
        else:
            print("User NOT found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_user(sys.argv[1])
    else:
        check_user("super.admin")
