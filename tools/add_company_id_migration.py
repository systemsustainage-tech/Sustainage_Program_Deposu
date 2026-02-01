import sqlite3
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from config.database import DB_PATH

def migrate_company_id():
    print(f"Migrating tables in {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    ignore_list = [
        'companies', 'sqlite_sequence', 'schema_migrations', 
        'supported_languages', 'sys_config'
    ]

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]

    for table in tables:
        if table in ignore_list:
            continue
            
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [r[1] for r in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print(f"Adding company_id to {table}...")
            try:
                # Add column with default 1 (System/Primary Company)
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN company_id INTEGER DEFAULT 1")
                
                # Add index for performance
                cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_company_id ON {table}(company_id)")
                print(f"  - Added company_id and index to {table}")
            except Exception as e:
                print(f"  - Error updating {table}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate_company_id()
