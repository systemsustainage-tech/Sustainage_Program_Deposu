
import sqlite3
import os

DB_PATH = '/var/www/sustainage/sustainage.db'

def inspect_table(conn, table_name):
    print(f"\n--- Structure of table: {table_name} ---")
    try:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if not columns:
            print(f"Table '{table_name}' does not exist.")
        else:
            for col in columns:
                # cid, name, type, notnull, dflt_value, pk
                print(f"  - {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Error inspecting {table_name}: {e}")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        tables_to_check = [
            'carbon_emissions', 
            'water_consumption', 
            'waste_generation', 
            'ungc_compliance',
            'ceo_messages',
            'companies'
        ]
        
        for table in tables_to_check:
            inspect_table(conn, table)
            
        conn.close()
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    main()
