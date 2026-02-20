import sqlite3
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Default DB Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')

# Global tables that should NOT have company_id
GLOBAL_TABLES = {
    'sqlite_sequence', 'alembic_version', 'sqlite_stat1', 
    'roles', 'permissions', 'role_permissions', 'user_roles',
    'companies', 'users', # users usually have company_id but sometimes are global. Let's check.
    # users table in this system has company_id according to previous searches, but maybe it's optional?
    # Actually, in multi-tenant, users usually belong to a company.
    # But 'companies' table definitely doesn't have company_id (it IS the company).
    'schema_migrations', 'audit_logs', # audit_logs might have company_id but maybe not required for system logs
    'system_settings', 'languages', 'translations'
}

def check_and_fix_schema(db_path):
    if not os.path.exists(db_path):
        logging.error(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]

        for table in tables:
            if table in GLOBAL_TABLES:
                continue
            
            # Check if table has company_id
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row['name'] for row in cursor.fetchall()]
            
            # Special check for survey_questions schema conflict
            if table == 'survey_questions':
                logging.info("Checking survey_questions schema compatibility...")
                if 'template_id' not in columns and 'survey_id' in columns:
                    logging.warning("survey_questions has survey_id but missing template_id. Adding template_id for compatibility.")
                    try:
                        cursor.execute("ALTER TABLE survey_questions ADD COLUMN template_id INTEGER")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_survey_questions_template_id ON survey_questions (template_id)")
                    except Exception as e:
                        logging.error(f"Failed to add template_id to survey_questions: {e}")
                
                elif 'survey_id' not in columns and 'template_id' in columns:
                    logging.warning("survey_questions has template_id but missing survey_id. Adding survey_id for compatibility.")
                    try:
                        cursor.execute("ALTER TABLE survey_questions ADD COLUMN survey_id INTEGER")
                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_survey_questions_survey_id ON survey_questions (survey_id)")
                    except Exception as e:
                        logging.error(f"Failed to add survey_id to survey_questions: {e}")

            if 'company_id' not in columns:
                logging.warning(f"Table '{table}' is missing 'company_id'. Adding it...")
                try:
                    # Add column with default value 1 (assuming ID 1 is the default/admin company)
                    # or NULL. Safe to default to 1 for migration.
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN company_id INTEGER DEFAULT 1")
                    
                    # Add index for performance
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_company_id ON {table} (company_id)")
                    
                    logging.info(f"Fixed '{table}': Added company_id and index.")
                except Exception as e:
                    logging.error(f"Failed to fix '{table}': {e}")
            else:
                # Ensure index exists
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_company_id ON {table} (company_id)")
                except Exception as e:
                    logging.warning(f"Could not create index for {table}: {e}")

        conn.commit()
        logging.info("Schema check completed.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        DB_PATH = sys.argv[1]
    
    print(f"Checking schema at: {DB_PATH}")
    check_and_fix_schema(DB_PATH)
