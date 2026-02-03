import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def migrate_multitenancy():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. support_replies
        logging.info("Checking support_replies...")
        cursor.execute("PRAGMA table_info(support_replies)")
        columns = [c[1] for c in cursor.fetchall()]
        if 'company_id' not in columns:
            logging.info("Adding company_id to support_replies...")
            cursor.execute("ALTER TABLE support_replies ADD COLUMN company_id INTEGER")
            
            # Backfill from support_tickets
            logging.info("Backfilling support_replies.company_id from support_tickets...")
            cursor.execute("""
                UPDATE support_replies 
                SET company_id = (
                    SELECT company_id 
                    FROM support_tickets 
                    WHERE support_tickets.id = support_replies.ticket_id
                )
            """)
            conn.commit()
            logging.info("support_replies migrated.")
        else:
            logging.info("support_replies already has company_id.")

        # 2. password_reset_tokens
        logging.info("Checking password_reset_tokens...")
        cursor.execute("PRAGMA table_info(password_reset_tokens)")
        columns = [c[1] for c in cursor.fetchall()]
        if 'company_id' not in columns:
            logging.info("Adding company_id to password_reset_tokens...")
            cursor.execute("ALTER TABLE password_reset_tokens ADD COLUMN company_id INTEGER")
            
            # Backfill from users
            logging.info("Backfilling password_reset_tokens.company_id from users...")
            cursor.execute("""
                UPDATE password_reset_tokens 
                SET company_id = (
                    SELECT company_id 
                    FROM users 
                    WHERE users.id = password_reset_tokens.user_id
                )
            """)
            conn.commit()
            logging.info("password_reset_tokens migrated.")
        else:
            logging.info("password_reset_tokens already has company_id.")

        # 3. temp_access_tokens
        logging.info("Checking temp_access_tokens...")
        cursor.execute("PRAGMA table_info(temp_access_tokens)")
        columns = [c[1] for c in cursor.fetchall()]
        if 'company_id' not in columns:
            logging.info("Adding company_id to temp_access_tokens...")
            cursor.execute("ALTER TABLE temp_access_tokens ADD COLUMN company_id INTEGER")
            
            # Backfill from users
            logging.info("Backfilling temp_access_tokens.company_id from users...")
            cursor.execute("""
                UPDATE temp_access_tokens 
                SET company_id = (
                    SELECT company_id 
                    FROM users 
                    WHERE users.id = temp_access_tokens.user_id
                )
            """)
            conn.commit()
            logging.info("temp_access_tokens migrated.")
        else:
            logging.info("temp_access_tokens already has company_id.")
            
        logging.info("Migration completed successfully.")

    except Exception as e:
        logging.error(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_multitenancy()
