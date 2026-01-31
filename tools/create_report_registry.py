import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def create_table():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating report_registry table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            module_code TEXT NOT NULL,
            report_name TEXT NOT NULL,
            report_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            reporting_period TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP,
            access_count INTEGER DEFAULT 0,
            tags TEXT,
            description TEXT
        )
    """)

    print("Creating companies table if not exists...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sector TEXT,
            country TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("Creating company_details_gri table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_details_gri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL UNIQUE,
            legal_name TEXT,
            address TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            founded_year INTEGER,
            employee_count INTEGER,
            description TEXT,
            mission TEXT,
            vision TEXT,
            tax_id TEXT,
            sector_details TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    conn.commit()
    print("Tables created.")
    
    # Verify
    for table in ['report_registry', 'companies', 'company_details_gri']:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cursor.fetchone():
            print(f"Verification: Table {table} exists.")
        else:
            print(f"Verification: Table {table} NOT found.")
        
    conn.close()

if __name__ == '__main__':
    create_table()
