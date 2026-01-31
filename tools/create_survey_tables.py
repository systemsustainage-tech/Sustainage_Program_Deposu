import sqlite3
import os

DB_PATH = '/var/www/sustainage/sustainage.db'

def create_survey_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        # Optionally create DB if it doesn't exist
        # return 

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print(f"Connected to {DB_PATH}")
        
        # 1. Survey Templates
        print("Creating survey_templates...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_templates (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'Genel',
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Survey Questions
        print("Creating survey_questions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_questions (
                id INTEGER PRIMARY KEY,
                template_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL, -- multiple_choice, scale, text, boolean
                weight REAL DEFAULT 1.0,
                category TEXT,
                sdg_mapping TEXT,
                options TEXT, -- JSON string for options
                is_required INTEGER DEFAULT 0,
                FOREIGN KEY(template_id) REFERENCES survey_templates(id) ON DELETE CASCADE
            )
        """)
        
        # 3. Survey Responses
        print("Creating survey_responses...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_responses (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                response_value TEXT,
                score REAL DEFAULT 0,
                response_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY(question_id) REFERENCES survey_questions(id) ON DELETE CASCADE
            )
        """)
        
        # 4. User Surveys (if needed for assigning surveys to users)
        print("Creating user_surveys...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                template_id INTEGER NOT NULL,
                company_id INTEGER,
                status TEXT DEFAULT 'pending', -- pending, in_progress, completed
                assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_date TIMESTAMP,
                score REAL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (template_id) REFERENCES survey_templates(id)
            )
        """)

        conn.commit()
        print("Tables created successfully.")
        
        # Check columns
        cursor.execute("PRAGMA table_info(survey_questions)")
        cols = [row[1] for row in cursor.fetchall()]
        print(f"Verified survey_questions columns: {cols}")
        
        conn.close()
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_survey_tables()
