import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def inspect_db():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables:")
    for table in tables:
        t_name = table[0]
        print(f"\nTable: {t_name}")
        cursor.execute(f"PRAGMA table_info({t_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

    conn.close()

if __name__ == "__main__":
    inspect_db()
