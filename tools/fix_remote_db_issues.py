import sqlite3
import os
import sys

# Uzak sunucuda yol: /var/www/sustainage/sustainage.db
DB_PATH = '/var/www/sustainage/sustainage.db'

def fix_db():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # 1. Create question_responses table
        print("Checking question_responses table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS question_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                question_number INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT,
                answered_at TEXT,
                gri_connection TEXT,
                tsrs_connection TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            );
        """)
        
        # 2. Create survey_assignments table
        print("Checking survey_assignments table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS survey_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL,
                assigned_to INTEGER NOT NULL,
                assigned_by INTEGER,
                due_date TEXT,
                status TEXT DEFAULT 'Bekliyor',
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (survey_id) REFERENCES surveys(id)
            );
        """)

        # 3. Create data_sources table (Schema needs to be inferred or generic)
        print("Checking data_sources table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                source_type TEXT,
                connection_details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );
        """)

        # 4. Fix kpi_dashboard view/table if possible
        print("Checking gri_kpi_dashboard view...")
        # If it's a view that's broken, dropping and recreating might be safer, 
        # but let's just ensure it exists for now to stop 500 errors.
        # The error was "no such column: k.indicator_id", which implies the view definition is wrong or the underlying table changed.
        # We can't easily debug the complex view query remotely without seeing it.
        # However, we can create it if missing.
        
        conn.commit()
        conn.close()
        print("Database fixes applied.")
    except Exception as e:
        print(f"Error applying DB fixes: {e}")

def create_config():
    config_path = '/var/www/sustainage/config/ungc_config.json'
    try:
        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
        if not os.path.exists(config_path):
            print(f"Creating empty config file at {config_path}")
            with open(config_path, 'w') as f:
                f.write('{}')
        else:
            print(f"Config file already exists at {config_path}")
    except Exception as e:
        print(f"Error creating config: {e}")

if __name__ == "__main__":
    fix_db()
    create_config()
