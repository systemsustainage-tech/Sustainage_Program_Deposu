import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import get_db_path
import sqlite3

DB_PATH = get_db_path()

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("Users Table Columns:")
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
