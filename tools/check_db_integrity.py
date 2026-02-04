import sqlite3
import sys

db_path = 'backend/data/sdg_desktop.sqlite'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check;")
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == 'ok':
        print("Database integrity check passed.")
        sys.exit(0)
    else:
        print(f"Database integrity check failed: {result}")
        sys.exit(1)
except Exception as e:
    print(f"Error checking database: {e}")
    sys.exit(1)
