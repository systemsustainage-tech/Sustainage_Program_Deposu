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
    
    # 1. Fix taxonomy_activities (previously misidentified as eu_taxonomy_data)
    try:
        logging.info("Checking taxonomy_activities schema...")
        cursor.execute("PRAGMA table_info(taxonomy_activities)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # List of columns to check/add
        cols_to_add = [
            ('turnover_aligned', 'REAL DEFAULT 0'),
            ('capex_aligned', 'REAL DEFAULT 0'),
            ('opex_aligned', 'REAL DEFAULT 0'),
            ('turnover_amount', 'REAL DEFAULT 0'),
            ('capex_amount', 'REAL DEFAULT 0'),
            ('opex_amount', 'REAL DEFAULT 0')
        ]
        
        if not columns:
             logging.error("Table taxonomy_activities does not exist!")
        else:
            for col_name, col_type in cols_to_add:
                if col_name not in columns:
                    logging.info(f"Adding '{col_name}' column to taxonomy_activities...")
                    cursor.execute(f"ALTER TABLE taxonomy_activities ADD COLUMN {col_name} {col_type}")
                    logging.info(f"Column '{col_name}' added.")
                else:
                    logging.info(f"'{col_name}' column already exists in taxonomy_activities.")
    except Exception as e:
        logging.error(f"Error fixing taxonomy_activities: {e}")

    # 2. Fix csrd_materiality (previously misidentified as csrd_records)
    try:
        logging.info("Checking csrd_materiality schema...")
        cursor.execute("PRAGMA table_info(csrd_materiality)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if not columns:
             logging.error("Table csrd_materiality does not exist!")
        else:
            if 'created_at' not in columns:
                logging.info("Adding 'created_at' column to csrd_materiality...")
                cursor.execute("ALTER TABLE csrd_materiality ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                logging.info("Column 'created_at' added.")
            else:
                logging.info("'created_at' column already exists in csrd_materiality.")
    except Exception as e:
        logging.error(f"Error fixing csrd_materiality: {e}")

    conn.commit()
    conn.close()
    logging.info("Schema fix v3 completed.")

if __name__ == "__main__":
    fix_schema()
