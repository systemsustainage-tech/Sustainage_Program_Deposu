import sqlite3
import os

DB_PATH = os.path.join('backend', 'data', 'sdg_desktop.sqlite')

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['waste_records', 'water_consumption', 'suppliers', 'supply_chain_metrics']
    
    for table in tables:
        print(f"--- Schema for {table} ---")
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            if columns:
                for col in columns:
                    print(col)
            else:
                print("Table not found.")
        except Exception as e:
            print(f"Error: {e}")
        print("\n")
        
    conn.close()

if __name__ == "__main__":
    check_schema()
