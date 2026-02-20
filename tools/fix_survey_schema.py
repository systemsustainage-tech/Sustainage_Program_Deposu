import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = os.path.join(os.getcwd(), 'backend', 'data', 'sdg_desktop.sqlite')

def fix_survey_questions_schema():
    """
    survey_questions tablosundaki survey_id sütununu nullable yapar.
    Mevcut tabloyu yedekler, yeni tabloyu oluşturur ve verileri aktarır.
    """
    if not os.path.exists(DB_PATH):
        logging.error(f"Veritabanı bulunamadı: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        logging.info("Checking survey_questions schema...")
        cursor.execute("PRAGMA table_info(survey_questions)")
        columns = cursor.fetchall()
        
        survey_id_info = next((c for c in columns if c[1] == 'survey_id'), None)
        
        if survey_id_info and survey_id_info[3] == 1: # notnull == 1
            logging.info("survey_id is NOT NULL. Fixing...")
            
            # 1. Rename existing table
            cursor.execute("ALTER TABLE survey_questions RENAME TO survey_questions_old")
            
            # 2. Create new table with nullable survey_id
            # Note: We keep other columns as they were in the DB check
            # (id, survey_id, category, question_text, question_type, options, is_required, display_order, created_at, company_id, template_id)
            cursor.execute("""
                CREATE TABLE survey_questions (
                    id INTEGER PRIMARY KEY,
                    survey_id INTEGER, -- Nullable now
                    category TEXT DEFAULT 'General',
                    question_text TEXT,
                    question_type TEXT DEFAULT 'scale_1_5',
                    options TEXT,
                    is_required BOOLEAN DEFAULT 1,
                    display_order INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    company_id INTEGER DEFAULT 1,
                    template_id INTEGER
                )
            """)
            
            # 3. Copy data
            # We need to list columns explicitly to avoid mismatch if schema changed slightly
            cols = "id, survey_id, category, question_text, question_type, options, is_required, display_order, created_at, company_id, template_id"
            cursor.execute(f"INSERT INTO survey_questions ({cols}) SELECT {cols} FROM survey_questions_old")
            
            # 4. Drop old table
            cursor.execute("DROP TABLE survey_questions_old")
            
            conn.commit()
            logging.info("survey_questions schema fixed.")
        else:
            logging.info("survey_id is already nullable or table not found.")

    except Exception as e:
        logging.error(f"Error fixing survey_questions: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_user_survey_responses_table():
    """
    SurveyBuilder için user_survey_responses tablosunu oluşturur.
    survey_responses tablosu Materiality Survey tarafından kullanıldığı için çakışmayı önler.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        logging.info("Checking/Creating user_survey_responses table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_survey_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER DEFAULT 1,
                user_survey_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                response_value TEXT,
                response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_survey_id) REFERENCES user_surveys(id),
                FOREIGN KEY (question_id) REFERENCES survey_questions(id)
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_survey_responses_company_id ON user_survey_responses (company_id)")
        
        conn.commit()
        logging.info("user_survey_responses table checked/created.")
        
    except Exception as e:
        logging.error(f"Error creating user_survey_responses: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_survey_questions_schema()
    create_user_survey_responses_table()
