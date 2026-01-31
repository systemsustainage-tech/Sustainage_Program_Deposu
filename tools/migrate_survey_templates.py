import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = os.path.join('backend', 'data', 'sdg_desktop.sqlite')

def migrate_templates():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check current state
        cursor.execute("SELECT COUNT(*) FROM survey_templates WHERE company_id = 1")
        count_1 = cursor.fetchone()[0]
        logging.info(f"Found {count_1} templates with company_id=1")
        
        if count_1 > 0:
            logging.info("Migrating templates with company_id=1 to company_id=NULL (Standard Templates)...")
            cursor.execute("UPDATE survey_templates SET company_id = NULL WHERE company_id = 1")
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM survey_templates WHERE company_id IS NULL")
            count_null = cursor.fetchone()[0]
            logging.info(f"Migration complete. Found {count_null} templates with company_id=NULL")
        else:
            logging.info("No templates to migrate or already migrated.")
            
        conn.close()
        
    except Exception as e:
        logging.error(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_templates()
