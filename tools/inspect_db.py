import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

DB_PATH = 'c:/SDG/temp_remote_sdg.db'

def main():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get table info for users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        logging.info("Users table columns:")
        for col in columns:
            logging.info(col)
            
        # Get one user
        cursor.execute("SELECT * FROM users LIMIT 1")
        user = cursor.fetchone()
        logging.info(f"Sample user: {user}")
        
        conn.close()
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    main()
