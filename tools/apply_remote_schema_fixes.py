import sqlite3
import os
import sys
import logging

# Hardcoded Remote DB Path (as per instructions)
# Or try to detect
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
# Fallback if that doesn't exist (e.g. running locally for test)
if not os.path.exists(DB_PATH):
    # Try local dev path
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'sdg_desktop.sqlite')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def apply_fixes():
    logging.info(f"Applying schema fixes to: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        logging.error("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        # 1. survey_responses fixes
        logging.info("Checking survey_responses...")
        try:
            cur = conn.execute("PRAGMA table_info(survey_responses)")
            columns = [row['name'] for row in cur.fetchall()]
            
            if 'user_agent' not in columns:
                logging.info("Adding user_agent to survey_responses")
                conn.execute("ALTER TABLE survey_responses ADD COLUMN user_agent TEXT")
                
            if 'ip_address' not in columns:
                logging.info("Adding ip_address to survey_responses")
                conn.execute("ALTER TABLE survey_responses ADD COLUMN ip_address TEXT")
        except Exception as e:
            logging.error(f"Error checking survey_responses: {e}")

        # 2. survey_answers fixes
        logging.info("Checking survey_answers...")
        try:
            cur = conn.execute("PRAGMA table_info(survey_answers)")
            columns = [row['name'] for row in cur.fetchall()]
            
            if 'answer_text' not in columns:
                logging.info("Adding answer_text to survey_answers")
                conn.execute("ALTER TABLE survey_answers ADD COLUMN answer_text TEXT")
                
            if 'score' not in columns:
                logging.info("Adding score to survey_answers")
                conn.execute("ALTER TABLE survey_answers ADD COLUMN score INTEGER")
        except Exception as e:
            logging.error(f"Error checking survey_answers: {e}")

        conn.commit()
        logging.info("Schema fixes applied successfully.")
        
    except Exception as e:
        logging.error(f"Global error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    apply_fixes()
