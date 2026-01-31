import sqlite3
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# DB Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')

def isolate_survey_responses():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    logging.info("Starting survey responses isolation...")

    # 1. Create tables if they don't exist (using correct schema)
    # survey_responses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            respondent_name TEXT,
            respondent_email TEXT,
            respondent_company TEXT,
            respondent_department TEXT,
            stakeholder_group TEXT,
            ip_address TEXT,
            user_agent TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            company_id INTEGER DEFAULT 1,
            FOREIGN KEY (survey_id) REFERENCES online_surveys(id) ON DELETE CASCADE
        )
    """)
    logging.info("Created/Verified survey_responses table")

    # survey_answers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answer_text TEXT,
            score INTEGER,
            company_id INTEGER DEFAULT 1,
            FOREIGN KEY (response_id) REFERENCES survey_responses(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES survey_questions(id) ON DELETE CASCADE
        )
    """)
    logging.info("Created/Verified survey_answers table")

    # 2. Add company_id column if it doesn't exist (for existing tables)
    def add_column_if_missing(table, col, dtype="INTEGER DEFAULT 1"):
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [c[1] for c in cursor.fetchall()]
            if col not in cols:
                logging.info(f"Adding {col} to {table}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error checking/adding {col} to {table}: {e}")
            return False

    add_column_if_missing('survey_responses', 'company_id')
    add_column_if_missing('survey_answers', 'company_id')
    add_column_if_missing('survey_responses', 'user_agent', 'TEXT') # Ensure user_agent exists too

    # 3. Backfill company_id from online_surveys
    # Link survey_responses -> online_surveys -> company_id
    try:
        logging.info("Backfilling survey_responses.company_id...")
        cursor.execute("""
            UPDATE survey_responses
            SET company_id = (
                SELECT company_id FROM online_surveys 
                WHERE online_surveys.id = survey_responses.survey_id
            )
            WHERE company_id IS NULL OR company_id = 1
        """)
        logging.info(f"Backfilled survey_responses: {cursor.rowcount} rows")
        
        # Link survey_answers -> survey_responses -> company_id
        logging.info("Backfilling survey_answers.company_id...")
        cursor.execute("""
            UPDATE survey_answers
            SET company_id = (
                SELECT company_id FROM survey_responses
                WHERE survey_responses.response_id = survey_answers.response_id
            )
            WHERE company_id IS NULL OR company_id = 1
        """)
        logging.info(f"Backfilled survey_answers: {cursor.rowcount} rows")
        
        conn.commit()
    except Exception as e:
        logging.error(f"Error backfilling data: {e}")
        conn.rollback()

    conn.close()
    logging.info("Survey isolation complete.")

if __name__ == "__main__":
    isolate_survey_responses()
