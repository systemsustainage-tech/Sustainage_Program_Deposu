import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def check_lca_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['lca_products', 'lca_assessments', 'lca_entries']
    
    for table in tables:
        print(f"--- Checking {table} ---")
        try:
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
            row = cursor.fetchone()
            if row:
                print(row[0])
            else:
                print(f"Table {table} does NOT exist.")
        except Exception as e:
            print(f"Error checking {table}: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_lca_schema()
