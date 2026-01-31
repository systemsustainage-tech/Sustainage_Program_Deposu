import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    tables_to_check = ['employee_satisfaction', 'community_investment']
    
    for table_name in tables_to_check:
        print(f"Checking {table_name} table...")
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table = cur.fetchone()
        
        if table:
            print(f"Table '{table_name}' EXISTS.")
            
            # Check columns
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = cur.fetchall()
            print("Columns:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
        else:
            print(f"Table '{table_name}' DOES NOT EXIST.")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
