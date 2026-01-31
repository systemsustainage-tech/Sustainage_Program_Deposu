
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def create_sample_survey():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for demographics_config column
    cursor.execute("PRAGMA table_info(online_surveys)")
    cols = [row[1] for row in cursor.fetchall()]
    if 'demographics_config' not in cols:
        print("Adding demographics_config column...")
        cursor.execute("ALTER TABLE online_surveys ADD COLUMN demographics_config TEXT DEFAULT '{}'")
        conn.commit()

    # Check if exists
    cursor.execute("SELECT id FROM online_surveys WHERE survey_link = '/survey/sample_survey'")
    row = cursor.fetchone()
    
    if row:
        print("Sample survey already exists. ID:", row[0])
        survey_id = row[0]
        
        # Ensure it is active
        cursor.execute("UPDATE online_surveys SET is_active=1 WHERE id=?", (survey_id,))
        conn.commit()
    else:
        print("Creating sample survey...")
        cursor.execute("""
            INSERT INTO online_surveys (
                company_id, survey_title, survey_description, target_groups, 
                survey_link, start_date, end_date, is_active, demographics_config
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 
            "Örnek Sürdürülebilirlik Anketi", 
            "Bu bir örnek ankettir. Lütfen soruları yanıtlayınız.", 
            "All", 
            "/survey/sample_survey", 
            datetime.now().strftime('%Y-%m-%d'), 
            "2030-12-31", 
            1, 
            json.dumps({"require_name": True, "require_email": True, "require_company": True, "require_department": True})
        ))
        survey_id = cursor.lastrowid
        print("Created survey with ID:", survey_id)

    # Check questions
    cursor.execute("SELECT count(*) FROM survey_questions WHERE survey_id = ?", (survey_id,))
    q_count = cursor.fetchone()[0]
    
    if q_count == 0:
        print("Adding questions...")
        questions = [
            ("Environmental", "Şirketinizin karbon ayak izini ölçüyor musunuz?", "yes_no"),
            ("Environmental", "Yenilenebilir enerji kullanıyor musunuz?", "yes_no"),
            ("Social", "Çalışan memnuniyeti anketi yapıyor musunuz?", "yes_no"),
            ("Governance", "Yönetim kurulunda sürdürülebilirlik temsilcisi var mı?", "yes_no"),
            ("General", "Sürdürülebilirlik hedefleriniz nelerdir?", "text")
        ]
        
        for i, (cat, text, qtype) in enumerate(questions):
            cursor.execute("""
                INSERT INTO survey_questions (survey_id, company_id, question_text, question_type, category, display_order)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (survey_id, 1, text, qtype, cat, i+1))
        
        conn.commit()
        print("Questions added.")
    else:
        print(f"Survey has {q_count} questions.")
        
    conn.close()

if __name__ == "__main__":
    create_sample_survey()
