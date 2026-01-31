import sqlite3
import os

# Dynamic DB path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Updating survey schema...")
    
    # 1. Update online_surveys table (add demographics_config if not exists)
    try:
        cursor.execute("ALTER TABLE online_surveys ADD COLUMN demographics_config TEXT DEFAULT '{}'")
        print("Added demographics_config column to online_surveys")
    except sqlite3.OperationalError:
        print("demographics_config column already exists")

    try:
        cursor.execute("ALTER TABLE online_surveys ADD COLUMN status TEXT DEFAULT 'draft'")
        print("Added status column to online_surveys")
    except sqlite3.OperationalError:
        print("status column already exists")
        
    # 2. Check for critical columns in survey_questions before creation
    try:
        cursor.execute("PRAGMA table_info(survey_questions)")
        columns = [col[1] for col in cursor.fetchall()]
        if columns and 'survey_id' not in columns:
            print("CRITICAL: survey_questions table exists but missing survey_id. Dropping table to recreate...")
            cursor.execute("DROP TABLE survey_questions")
    except Exception as e:
        print(f"Error checking survey_questions schema: {e}")

    # 2. Create survey_questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            category TEXT DEFAULT 'General', -- Environmental, Social, Governance, General
            question_text TEXT NOT NULL,
            question_type TEXT DEFAULT 'scale_1_5', -- scale_1_5, text, boolean, multi_choice
            options TEXT, -- JSON for multi_choice options
            is_required BOOLEAN DEFAULT 1,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (survey_id) REFERENCES online_surveys(id) ON DELETE CASCADE
        )
    """)
    
    # Check and add columns if missing in survey_questions
    try:
        cursor.execute("ALTER TABLE survey_questions ADD COLUMN category TEXT DEFAULT 'General'")
        print("Added category column to survey_questions")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE survey_questions ADD COLUMN question_type TEXT DEFAULT 'scale_1_5'")
        print("Added question_type column to survey_questions")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE survey_questions ADD COLUMN is_required BOOLEAN DEFAULT 1")
        print("Added is_required column to survey_questions")
    except sqlite3.OperationalError:
        pass

    print("Created/Verified survey_questions table")
    
    # 3. Create survey_responses table (Detailed respondent info)
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
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (survey_id) REFERENCES online_surveys(id) ON DELETE CASCADE
        )
    """)
    print("Created/Verified survey_responses table")
    
    # 4. Create survey_answers table (Detailed answers)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answer_value TEXT, -- Stores '5', 'Yes', 'Some text' etc.
            FOREIGN KEY (response_id) REFERENCES survey_responses(id) ON DELETE CASCADE,
            FOREIGN KEY (question_id) REFERENCES survey_questions(id) ON DELETE CASCADE
        )
    """)
    print("Created/Verified survey_answers table")
    
    conn.commit()
    conn.close()
    print("Schema update complete.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
    else:
        update_schema()
