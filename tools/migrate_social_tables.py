import sqlite3
import os

DB_PATH = "/var/www/sustainage/data/sdg_desktop.sqlite"

def migrate_social():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ['hr_employees', 'ohs_incidents', 'training_records']
    
    print("--- Migrating Social Tables ---")
    
    for table in tables:
        try:
            # Check if column exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'company_id' not in columns:
                print(f"Adding company_id to {table}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN company_id INTEGER DEFAULT 1")
                print(f"Done.")
            else:
                print(f"company_id already exists in {table}.")
                
        except Exception as e:
            print(f"Error migrating {table}: {e}")
            
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_social()
