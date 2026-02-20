import sqlite3
import sys
import os

if os.name == 'nt':
    DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
else:
    DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

def check_table():
    print(f"Checking rate_limits in {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rate_limits'")
        if cursor.fetchone():
            print("Table 'rate_limits' EXISTS.")
        else:
            print("Table 'rate_limits' MISSING.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_table()
