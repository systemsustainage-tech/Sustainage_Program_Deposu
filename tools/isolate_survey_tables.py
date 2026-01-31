import sqlite3
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = 'c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'

def isolate_survey_tables():
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1. Check and add company_id to survey_templates
        logging.info("Checking survey_templates schema...")
        cursor.execute("PRAGMA table_info(survey_templates)")
        columns = [col['name'] for col in cursor.fetchall()]
        
        if 'company_id' not in columns:
            logging.info("Adding company_id to survey_templates...")
            cursor.execute("ALTER TABLE survey_templates ADD COLUMN company_id INTEGER DEFAULT 1")
            # Set default to 1 (System)
            cursor.execute("UPDATE survey_templates SET company_id = 1 WHERE company_id IS NULL")
        else:
            logging.info("survey_templates already has company_id.")

        # 2. Check and add company_id to survey_questions
        logging.info("Checking survey_questions schema...")
        cursor.execute("PRAGMA table_info(survey_questions)")
        columns = [col['name'] for col in cursor.fetchall()]
        
        if 'company_id' not in columns:
            logging.info("Adding company_id to survey_questions...")
            cursor.execute("ALTER TABLE survey_questions ADD COLUMN company_id INTEGER DEFAULT 1")
            
            # Populate company_id from online_surveys
            logging.info("Populating survey_questions.company_id from online_surveys...")
            
            # We need to join with online_surveys to get the correct company_id
            # SQLite doesn't support JOIN in UPDATE directly in a standard way that works for all versions easily,
            # but we can use a subquery or iterate. Given the likely small size, iteration is safe, or subquery.
            
            # Using subquery for update
            cursor.execute("""
                UPDATE survey_questions
                SET company_id = (
                    SELECT company_id 
                    FROM online_surveys 
                    WHERE online_surveys.id = survey_questions.survey_id
                )
                WHERE survey_id IN (SELECT id FROM online_surveys)
            """)
            
            # For templates (survey_id might be null? No, survey_questions usually link to survey_id)
            # Wait, survey_questions in this system seem to be linked to online_surveys (instances) OR templates?
            # Let's check schema again.
            # Schema: survey_questions(id, survey_id, ...)
            # Survey Builder code showed: survey_questions linked to template_id in 'survey_builder.py' 
            # BUT 'web_app.py' inserts into survey_questions with survey_id.
            # This suggests survey_questions table is used for BOTH or there are two tables?
            # 'survey_builder.py' creates table with 'template_id'.
            # 'web_app.py' inserts with 'survey_id'.
            # Let's check if survey_questions has 'template_id' column.
            
            cursor.execute("PRAGMA table_info(survey_questions)")
            cols = [c['name'] for c in cursor.fetchall()]
            has_template_id = 'template_id' in cols
            has_survey_id = 'survey_id' in cols
            
            logging.info(f"survey_questions columns: {cols}")
            
            if has_survey_id:
                logging.info("Updating based on survey_id link to online_surveys...")
                cursor.execute("""
                    UPDATE survey_questions
                    SET company_id = (
                        SELECT company_id 
                        FROM online_surveys 
                        WHERE online_surveys.id = survey_questions.survey_id
                    )
                    WHERE survey_id IS NOT NULL 
                    AND survey_id IN (SELECT id FROM online_surveys)
                """)
            
            if has_template_id:
                logging.info("Updating based on template_id link to survey_templates...")
                cursor.execute("""
                    UPDATE survey_questions
                    SET company_id = (
                        SELECT company_id 
                        FROM survey_templates 
                        WHERE survey_templates.id = survey_questions.template_id
                    )
                    WHERE template_id IS NOT NULL 
                    AND template_id IN (SELECT id FROM survey_templates)
                    AND (company_id IS NULL OR company_id = 1) 
                """)
                # Note: if it has both, survey_id usually takes precedence for an instance.
                
            # Handle orphans or defaults
            cursor.execute("UPDATE survey_questions SET company_id = 1 WHERE company_id IS NULL")
            
        else:
            logging.info("survey_questions already has company_id.")

        conn.commit()
        logging.info("Isolation updates completed successfully.")

    except Exception as e:
        logging.error(f"Error during isolation: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    isolate_survey_tables()
