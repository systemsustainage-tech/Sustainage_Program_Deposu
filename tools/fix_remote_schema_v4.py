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
    
    # Fix csrd_materiality with NULL default
    try:
        logging.info("Checking csrd_materiality schema...")
        cursor.execute("PRAGMA table_info(csrd_materiality)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if not columns:
             logging.error("Table csrd_materiality does not exist!")
        else:
            if 'created_at' not in columns:
                logging.info("Adding 'created_at' column to csrd_materiality (DEFAULT NULL)...")
                # SQLite doesn't allow non-constant default in ADD COLUMN. Using NULL or fixed string is safe.
                # We will handle timestamp in code.
                cursor.execute("ALTER TABLE csrd_materiality ADD COLUMN created_at TIMESTAMP DEFAULT NULL")
                logging.info("Column 'created_at' added.")
            else:
                logging.info("'created_at' column already exists in csrd_materiality.")
    except Exception as e:
        logging.error(f"Error fixing csrd_materiality: {e}")

    conn.commit()
    conn.close()
    logging.info("Schema fix v4 completed.")

if __name__ == "__main__":
    fix_schema()
