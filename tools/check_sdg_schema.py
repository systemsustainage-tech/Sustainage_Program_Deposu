import sqlite3
import os

db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ['sdg_goals', 'sdg_targets', 'sdg_indicators', 'sdg_responses']
    
    for table in tables:
        print(f"--- Schema for {table} ---")
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        result = cursor.fetchone()
        if result:
            print(result[0])
        else:
            print(f"Table {table} does not exist.")
    
    conn.close()
