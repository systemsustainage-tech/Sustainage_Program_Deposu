import sqlite3
import logging
import os
import sys

# Configuration
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    if not os.path.exists(DB_PATH):
        logging.error(f"DB not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        logging.info("Checking user_roles table...")
        cursor.execute("PRAGMA table_info(user_roles)")
        columns = [info[1] for info in cursor.fetchall()]
        logging.info(f"Columns: {columns}")
        
        if 'assigned_by' not in columns:
            logging.info("Adding 'assigned_by' column...")
            cursor.execute("ALTER TABLE user_roles ADD COLUMN assigned_by TEXT")
            conn.commit()
            logging.info("Column added.")
        else:
            logging.info("'assigned_by' column already exists.")
            
        conn.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
