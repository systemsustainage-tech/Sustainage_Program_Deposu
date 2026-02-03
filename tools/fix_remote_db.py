
import sqlite3
import os
import sys

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_db():
    print(f"Checking database at {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("Database file not found!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Check users table for company_id
        print("Checking 'users' table schema...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print("Adding 'company_id' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN company_id INTEGER DEFAULT 1")
            conn.commit()
            print("Added 'company_id' column.")
        else:
            print("'company_id' column already exists in 'users'.")

        # 2. Check employee_satisfaction table schema
        print("Checking 'employee_satisfaction' table schema...")
        cursor.execute("PRAGMA table_info(employee_satisfaction)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Check for 'average_score' vs 'satisfaction_score'
        if 'average_score' in columns and 'satisfaction_score' not in columns:
             print("Note: Table uses 'average_score' (Remote Schema).")
        elif 'satisfaction_score' in columns:
             print("Note: Table uses 'satisfaction_score' (Local Schema).")
        else:
             print("Warning: Neither 'average_score' nor 'satisfaction_score' found.")

        # 3. Ensure company_id=1 exists in companies table if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
        if cursor.fetchone():
             cursor.execute("SELECT count(*) FROM companies WHERE id=1")
             if cursor.fetchone()[0] == 0:
                 print("Inserting default company (id=1)...")
                 cursor.execute("INSERT INTO companies (id, name) VALUES (1, 'Demo Company')")
                 conn.commit()

        # 4. Create licenses table if not exists
        print("Checking 'licenses' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                license_key TEXT UNIQUE NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                max_users INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        conn.commit()
        print("Licenses table checked/created.")

        conn.close()
        print("Database fix completed.")

    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    fix_db()
