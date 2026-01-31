import sqlite3
import time

DB_PATH = '/var/www/sustainage/sustainage.db'

def unlock_admin():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        print("Unlocking admin account...")
        cur.execute("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = 'admin'")
        if cur.rowcount > 0:
            print("Admin account unlocked successfully.")
        else:
            print("Admin user not found.")
            
        # Also clear rate limits if any
        try:
            cur.execute("DELETE FROM rate_limits WHERE identifier = 'admin' OR identifier LIKE '127.0.0.1%' OR identifier LIKE '72.62.150.207%'")
            print("Rate limits cleared.")
        except Exception as e:
            print(f"Error clearing rate limits: {e}")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error unlocking admin: {e}")

if __name__ == '__main__':
    unlock_admin()
