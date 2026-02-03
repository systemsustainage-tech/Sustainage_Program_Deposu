import sqlite3
import os

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def check_mappings():
    if not os.path.exists(DB_PATH):
        print("Database not found")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'map_%'")
    tables = cursor.fetchall()
    
    print("Mapping Tables found:")
    for table in tables:
        t_name = table[0]
        cursor.execute(f"SELECT count(*) FROM {t_name}")
        count = cursor.fetchone()[0]
        print(f" - {t_name}: {count} rows")
        
        # Show schema
        cursor.execute(f"PRAGMA table_info({t_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"   Columns: {columns}")

    conn.close()

if __name__ == "__main__":
    check_mappings()
