import sqlite3
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# DB Path on remote server
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Fix audit_logs
    try:
        logging.info("Checking audit_logs schema...")
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'resource' not in columns:
            logging.info("Adding 'resource' column to audit_logs...")
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN resource TEXT")
            logging.info("Column 'resource' added.")
        else:
            logging.info("'resource' column already exists in audit_logs.")
    except Exception as e:
        logging.error(f"Error fixing audit_logs: {e}")

    # 2. Fix eu_taxonomy_data
    try:
        logging.info("Checking eu_taxonomy_data schema...")
        cursor.execute("PRAGMA table_info(eu_taxonomy_data)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'turnover_aligned' not in columns:
            logging.info("Adding 'turnover_aligned' column to eu_taxonomy_data...")
            cursor.execute("ALTER TABLE eu_taxonomy_data ADD COLUMN turnover_aligned REAL DEFAULT 0")
            logging.info("Column 'turnover_aligned' added.")
        else:
            logging.info("'turnover_aligned' column already exists in eu_taxonomy_data.")
    except Exception as e:
        logging.error(f"Error fixing eu_taxonomy_data: {e}")

    # 3. Fix csrd_records
    try:
        logging.info("Checking csrd_records schema...")
        cursor.execute("PRAGMA table_info(csrd_records)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'created_at' not in columns:
            logging.info("Adding 'created_at' column to csrd_records...")
            cursor.execute("ALTER TABLE csrd_records ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            logging.info("Column 'created_at' added.")
        else:
            logging.info("'created_at' column already exists in csrd_records.")
    except Exception as e:
        logging.error(f"Error fixing csrd_records: {e}")

    # 4. Fix sdg_goals
    try:
        logging.info("Checking sdg_goals schema...")
        cursor.execute("PRAGMA table_info(sdg_goals)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'sdg_no' not in columns:
            logging.info("Adding 'sdg_no' column to sdg_goals...")
            cursor.execute("ALTER TABLE sdg_goals ADD COLUMN sdg_no INTEGER")
            logging.info("Column 'sdg_no' added.")
        else:
            logging.info("'sdg_no' column already exists in sdg_goals.")
    except Exception as e:
        logging.error(f"Error fixing sdg_goals: {e}")

    conn.commit()
    conn.close()
    logging.info("Schema fix completed.")

if __name__ == "__main__":
    fix_schema()
