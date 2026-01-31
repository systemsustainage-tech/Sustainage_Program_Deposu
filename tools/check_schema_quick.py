import sqlite3
import os

# Correct path based on config/database.py
DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        tables = ['sdg_goals', 'system_settings', 'backup_history', 'audit_logs']
        for table in tables:
            print(f"\n--- Schema for {table} ---")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            if not columns:
                print("Table not found.")
            for col in columns:
                print(col)
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
