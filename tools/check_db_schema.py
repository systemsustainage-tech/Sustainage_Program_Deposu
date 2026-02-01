import sqlite3
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from config.database import DB_PATH

def check_schema():
    print(f"Checking schema in {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    
    missing_company_id = []
    
    ignore_list = ['sqlite_sequence', 'alembic_version', 'sqlite_stat1']
    
    print(f"Found {len(tables)} tables.")
    
    for table in tables:
        if table in ignore_list:
            continue
            
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [r[1] for r in cursor.fetchall()]
        
        if 'company_id' not in columns:
            missing_company_id.append(table)
            
    conn.close()
    
    if missing_company_id:
        print("\nTables MISSING company_id:")
        for t in missing_company_id:
            print(f" - {t}")
    else:
        print("\nAll relevant tables have company_id.")

if __name__ == "__main__":
    check_schema()
