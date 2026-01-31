
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fix_security_logs_table():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sdg_desktop.sqlite')
    logging.info(f"Connecting to database: {db_path}")
    
    if not os.path.exists(db_path):
        logging.error("Database file not found!")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Check existing columns
        cur.execute("PRAGMA table_info(security_logs)")
        columns = [info[1] for info in cur.fetchall()]
        logging.info(f"Existing columns: {columns}")
        
        # Drop table
        logging.info("Dropping security_logs table...")
        cur.execute("DROP TABLE IF EXISTS security_logs")
        
        # Recreate table with correct schema
        logging.info("Recreating security_logs table...")
        cur.execute("""
            CREATE TABLE security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                event_type TEXT,
                success INTEGER,
                ip_address TEXT,
                user_agent TEXT,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logging.info("Successfully recreated security_logs table.")
        
    except Exception as e:
        logging.error(f"Error fixing table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_security_logs_table()
