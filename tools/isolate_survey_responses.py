import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = 'sustainage.db'

def get_connection():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH)

def check_and_add_column(cursor, table, column, dtype="INTEGER DEFAULT 1"):
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if column not in columns:
            logging.info(f"Adding {column} to {table}...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {dtype}")
            return True
        else:
            logging.info(f"Column {column} already exists in {table}.")
            return False
    except Exception as e:
        logging.error(f"Error checking/adding column {column} to {table}: {e}")
        return False

def isolate_survey_responses():
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()

    try:
        # 1. survey_responses
        added = check_and_add_column(cursor, "survey_responses", "company_id")
        
        # Backfill strategy
        logging.info("Backfilling survey_responses.company_id...")
        
        # Check if survey_responses has survey_id
        cursor.execute("PRAGMA table_info(survey_responses)")
        resp_cols = [row[1] for row in cursor.fetchall()]
        
        if 'survey_id' in resp_cols:
            # Check if online_surveys exists and has company_id
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='online_surveys'")
            if cursor.fetchone():
                logging.info("Updating from online_surveys...")
                cursor.execute("""
                    UPDATE survey_responses 
                    SET company_id = (SELECT company_id FROM online_surveys WHERE online_surveys.id = survey_responses.survey_id)
                    WHERE survey_id IS NOT NULL AND company_id = 1
                """)
            
            # Check if surveys exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='surveys'")
            if cursor.fetchone():
                logging.info("Updating from surveys...")
                cursor.execute("""
                    UPDATE survey_responses 
                    SET company_id = (SELECT company_id FROM surveys WHERE surveys.id = survey_responses.survey_id)
                    WHERE survey_id IS NOT NULL AND company_id = 1
                """)

        elif 'user_survey_id' in resp_cols:
            # Check user_surveys
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_surveys'")
            if cursor.fetchone():
                logging.info("Updating from user_surveys...")
                cursor.execute("""
                    UPDATE survey_responses 
                    SET company_id = (SELECT company_id FROM user_surveys WHERE user_surveys.id = survey_responses.user_survey_id)
                    WHERE user_survey_id IS NOT NULL AND company_id = 1
                """)

        conn.commit()

        # 2. survey_answers
        # Assuming survey_answers links to survey_responses via response_id
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='survey_answers'")
        if cursor.fetchone():
            added_ans = check_and_add_column(cursor, "survey_answers", "company_id")
            
            logging.info("Backfilling survey_answers.company_id from survey_responses...")
            cursor.execute("""
                UPDATE survey_answers
                SET company_id = (SELECT company_id FROM survey_responses WHERE survey_responses.id = survey_answers.response_id)
                WHERE response_id IS NOT NULL AND (company_id IS NULL OR company_id = 1)
            """)
            conn.commit()
        else:
            logging.info("Table survey_answers not found.")

        logging.info("Survey isolation complete.")

    except Exception as e:
        logging.error(f"Error isolating surveys: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    isolate_survey_responses()
