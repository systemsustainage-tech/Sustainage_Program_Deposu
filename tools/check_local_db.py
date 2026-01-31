import sqlite3
import os
import sys

# Configure logging to print to stdout immediately
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stdout)

DB_PATH = 'c:/SDG/server/backend/data/sdg_desktop.sqlite'

def check_db():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logging.info(f"Tables: {[t[0] for t in tables]}")
        
        # Check counts for key tables
        key_tables = ['users', 'companies', 'reports', 'data_points']
        for table in key_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logging.info(f"Table '{table}': {count} rows")
            except sqlite3.OperationalError:
                logging.warning(f"Table '{table}' does not exist.")
                
        conn.close()
    except Exception as e:
        logging.error(f"Error checking database: {e}")

if __name__ == '__main__':
    check_db()
