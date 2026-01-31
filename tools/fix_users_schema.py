import sqlite3
import os
import sys

def fix_schema():
    db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    print(f"Fixing users schema in {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'is_locked' not in columns:
        print("Adding 'is_locked' column...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_locked BOOLEAN DEFAULT 0")
    else:
        print("'is_locked' column already exists.")
        
    conn.commit()
    conn.close()
    print("Schema fix complete.")

if __name__ == "__main__":
    fix_schema()
