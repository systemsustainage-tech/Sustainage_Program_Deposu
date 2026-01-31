import sqlite3
import os

DB_PATH = '/var/www/sustainage/data/sdg_desktop.sqlite'

def check_table_columns(table_name):
    print(f"Checking columns for table: {table_name}")
    try:
        if not os.path.exists(DB_PATH):
            print(f"Database not found at {DB_PATH}")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        if not columns:
            print(f"Table {table_name} not found or has no columns.")
        else:
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_table_columns("carbon_emissions")
    check_table_columns("waste_generation")
    check_table_columns("water_consumption")
    check_table_columns("energy_consumption")
