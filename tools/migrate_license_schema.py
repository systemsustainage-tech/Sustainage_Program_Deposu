import sqlite3
import os
import sys

# Define database path
if os.name == 'nt':
    DB_PATH = r'C:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
else:
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def migrate_licenses_table():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Connected to database: {DB_PATH}")
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(licenses)")
    columns = [info[1] for info in cursor.fetchall()]
    
    new_columns = {
        'allowed_ips': 'TEXT',
        'allowed_domains': 'TEXT',
        'usage_count': 'INTEGER DEFAULT 0',
        'last_usage_at': 'TIMESTAMP',
        'suspended_at': 'TIMESTAMP',
        'suspension_reason': 'TEXT'
    }
    
    for col, col_type in new_columns.items():
        if col not in columns:
            try:
                print(f"Adding column {col}...")
                cursor.execute(f"ALTER TABLE licenses ADD COLUMN {col} {col_type}")
                print(f"Column {col} added successfully.")
            except Exception as e:
                print(f"Error adding column {col}: {e}")
        else:
            print(f"Column {col} already exists.")
            
    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate_licenses_table()
