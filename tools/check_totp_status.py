import sqlite3
import os
import sys

def check_totp_status():
    # Default to remote path if on Linux/Remote, otherwise local
    db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    if os.name == 'nt':
        db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
        
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all columns
        cursor.execute("PRAGMA table_info(users)")
        columns_info = cursor.fetchall()
        columns = [row[1] for row in columns_info]
        
        print(f"Columns in users table: {columns}")

        if 'totp_secret_encrypted' in columns:
            cursor.execute("SELECT count(*) FROM users WHERE totp_secret_encrypted IS NOT NULL AND totp_secret_encrypted != ''")
            encrypted_count = cursor.fetchone()[0]
            print(f"Encrypted TOTP Secrets count: {encrypted_count}")
        else:
            print("FAIL: totp_secret_encrypted column MISSING.")

        if 'totp_secret' in columns:
            cursor.execute("SELECT count(*) FROM users WHERE totp_secret IS NOT NULL AND totp_secret != ''")
            legacy_count = cursor.fetchone()[0]
            print(f"Legacy TOTP Secrets count: {legacy_count}")
        else:
            print("INFO: totp_secret column (legacy) does not exist (cleaned up).")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_totp_status()
