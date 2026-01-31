
import sqlite3
import os

DB_PATH = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = ['sdg_goals', 'system_settings', 'audit_logs']
    
    for table in tables:
        print(f"\n--- Schema for {table} ---")
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            if not columns:
                print("Table not found.")
            else:
                found_company_id = False
                for col in columns:
                    print(col)
                    if col[1] == 'company_id':
                        found_company_id = True
                
                if found_company_id:
                    print(f"✅ {table} has company_id")
                else:
                    print(f"❌ {table} does NOT have company_id")
        except Exception as e:
            print(f"Error checking {table}: {e}")

    conn.close()

if __name__ == "__main__":
    check_schema()
