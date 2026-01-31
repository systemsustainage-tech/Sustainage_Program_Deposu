import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

DB_PATH = 'c:/SDG/temp_remote_sdg.db'

def main():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logging.info("Tables:")
        for t in tables:
            logging.info(t[0])
            
        # Check roles content
        try:
            logging.info("\nRoles:")
            cursor.execute("SELECT * FROM roles")
            roles = cursor.fetchall()
            for r in roles:
                logging.info(r)
        except Exception as e:
            logging.error(f"Error reading roles: {e}")
            
        # Check user_roles content
        try:
            logging.info("\nUser Roles:")
            cursor.execute("SELECT * FROM user_roles")
            urs = cursor.fetchall()
            for ur in urs:
                logging.info(ur)
        except Exception as e:
            logging.error(f"Error reading user_roles: {e}")
        
        conn.close()
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    main()
