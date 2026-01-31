
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Checking tcfd_financial_impact table...")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tcfd_financial_impact'")
    table = cur.fetchone()
    
    if table:
        print("Table 'tcfd_financial_impact' EXISTS.")
        
        # Check columns
        cur.execute("PRAGMA table_info(tcfd_financial_impact)")
        columns = cur.fetchall()
        print("Columns:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        required_columns = ['financial_impact', 'probability', 'time_horizon', 'scenario']
        existing_column_names = [col[1] for col in columns]
        
        missing = [c for c in required_columns if c not in existing_column_names]
        if missing:
            print(f"MISSING COLUMNS: {missing}")
        else:
            print("All required columns present.")
            
    else:
        print("Table 'tcfd_financial_impact' DOES NOT EXIST.")
        
    conn.close()

if __name__ == "__main__":
    check_schema()
