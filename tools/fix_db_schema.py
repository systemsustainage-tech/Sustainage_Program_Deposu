
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    print(f"Checking schema at {DB_PATH}...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Companies Table
        print("Checking companies table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sector TEXT,
                country TEXT,
                tax_number TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check columns
        cols = [info[1] for info in cursor.execute("PRAGMA table_info(companies)").fetchall()]
        if 'tax_number' not in cols:
            print("Adding tax_number column to companies...")
            cursor.execute("ALTER TABLE companies ADD COLUMN tax_number TEXT")
        if 'is_active' not in cols:
            print("Adding is_active column to companies...")
            cursor.execute("ALTER TABLE companies ADD COLUMN is_active BOOLEAN DEFAULT 1")
            
        # 2. Report Registry
        print("Checking report_registry table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                module_code TEXT,
                report_name TEXT,
                report_type TEXT,
                file_path TEXT,
                file_size INTEGER,
                reporting_period TEXT,
                description TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)

        # 3. GRI Table
        print("Checking company_details_gri table...")
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

        # 4. Waste Generation Table (Ensure period column)
        print("Checking waste_generation table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_generation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                period TEXT,
                waste_type TEXT,
                amount REAL,
                unit TEXT,
                disposal_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cols = [info[1] for info in cursor.execute("PRAGMA table_info(waste_generation)").fetchall()]
        if 'period' not in cols:
            print("Adding period column to waste_generation...")
            cursor.execute("ALTER TABLE waste_generation ADD COLUMN period TEXT")
        if 'amount' not in cols:
             print("Adding amount column to waste_generation...")
             cursor.execute("ALTER TABLE waste_generation ADD COLUMN amount REAL")
        
        # 5. Survey Templates Isolation
        print("Checking survey_templates table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER DEFAULT NULL
            )
        """)
        cols = [info[1] for info in cursor.execute("PRAGMA table_info(survey_templates)").fetchall()]
        if 'company_id' not in cols:
            print("Adding company_id to survey_templates...")
            cursor.execute("ALTER TABLE survey_templates ADD COLUMN company_id INTEGER DEFAULT NULL")

        # 6. Audit Logs Isolation
        print("Checking audit_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT,
                details TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER
            )
        """)
        cols = [info[1] for info in cursor.execute("PRAGMA table_info(audit_logs)").fetchall()]
        if 'company_id' not in cols:
            print("Adding company_id to audit_logs...")
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN company_id INTEGER")
            
        # 7. System Settings Isolation
        print("Checking system_settings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT,
                value TEXT,
                category TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                company_id INTEGER,
                PRIMARY KEY (key, company_id)
            )
        """)
        cols = [info[1] for info in cursor.execute("PRAGMA table_info(system_settings)").fetchall()]
        if 'company_id' not in cols:
            print("Adding company_id to system_settings...")
            # This is tricky because of PRIMARY KEY. 
            # SQLite doesn't support ADD COLUMN with PRIMARY KEY change easily.
            # For now just add the column if missing.
            cursor.execute("ALTER TABLE system_settings ADD COLUMN company_id INTEGER")

        conn.commit()
        conn.close()
        print("Schema check complete.")
        
    except Exception as e:
        print(f"Schema fix error: {e}")

if __name__ == "__main__":
    fix_schema()
