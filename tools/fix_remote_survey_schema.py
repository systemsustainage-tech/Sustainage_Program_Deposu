import sqlite3
import os
import sys

# Remote path
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print(f"Connected to {DB_PATH}")
        
        # 1. online_surveys
        print("Creating online_surveys...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS online_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                survey_title TEXT NOT NULL,
                survey_description TEXT,
                target_groups TEXT NOT NULL,
                survey_link TEXT UNIQUE NOT NULL,
                start_date DATE,
                end_date DATE,
                total_questions INTEGER DEFAULT 0,
                response_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                demographics_config TEXT DEFAULT '{}',
                status TEXT DEFAULT 'draft',
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # 2. survey_questions
        print("Creating survey_questions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL,
                company_id INTEGER,
                question_text TEXT NOT NULL,
                question_type TEXT DEFAULT 'scale_1_5',
                category TEXT DEFAULT 'General',
                options TEXT,
                is_required BOOLEAN DEFAULT 1,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (survey_id) REFERENCES online_surveys(id) ON DELETE CASCADE
            )
        """)
        
        # 3. survey_responses
        print("Creating survey_responses...")
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
                company_id INTEGER,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (survey_id) REFERENCES online_surveys(id) ON DELETE CASCADE
            )
        """)
        
        # 4. survey_answers
        print("Creating survey_answers...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                response_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                answer_text TEXT,
                score INTEGER,
                company_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (response_id) REFERENCES survey_responses(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES survey_questions(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        print("Tables created successfully.")
        
        # Check if we need to add a sample survey
        cursor.execute("SELECT count(*) FROM online_surveys")
        count = cursor.fetchone()[0]
        if count == 0:
            print("Adding sample survey...")
            import uuid
            token = "sample_survey"
            link = f"/survey/{token}"
            company_id = 1
            
            cursor.execute("""
                INSERT INTO online_surveys (
                    company_id, survey_title, survey_description, target_groups,
                    survey_link, is_active, status
                ) VALUES (?, ?, ?, ?, ?, 1, 'active')
            """, (company_id, "Örnek Sürdürülebilirlik Anketi", "Bu bir örnek ankettir.", "Employees", link))
            
            survey_id = cursor.lastrowid
            
            # Add sample questions
            questions = [
                ("Şirketimizin çevresel hedeflerini biliyor musunuz?", "scale_1_5", "Çevre"),
                ("İş yerinde geri dönüşüm kutularını kullanıyor musunuz?", "boolean", "Atık Yönetimi"),
                ("Sürdürülebilirlik konusunda önerileriniz nelerdir?", "text", "Genel")
            ]
            
            for i, (text, qtype, cat) in enumerate(questions):
                cursor.execute("""
                    INSERT INTO survey_questions (survey_id, company_id, question_text, question_type, category, display_order)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (survey_id, company_id, text, qtype, cat, i+1))
                
            conn.commit()
            print("Sample survey added.")

        conn.close()
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_schema()
