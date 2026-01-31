import os
import sqlite3
import sys
import random
import uuid
from datetime import datetime, timedelta

def get_db_path():
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from config.database import DB_PATH
        if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
            return '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
        return DB_PATH
    except Exception:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.name == 'nt':
            return os.path.join(base_dir, 'backend', 'data', 'sdg_desktop.sqlite')
        if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
            return '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
        return '/var/www/sustainage/sustainage.db'

def ensure_schema(db_path: str) -> None:
    # Schema is already managed by app/migrations, we just assume it exists or use what's there.
    # We won't create tables here to avoid conflict, just use existing ones.
    pass

def create_sample_survey(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    company_id = 1 # Default test company
    
    # Check if survey exists
    cur.execute("SELECT id FROM online_surveys WHERE survey_title=? AND company_id=?", ("Örnek Anket 1", company_id))
    row = cur.fetchone()
    
    if row:
        survey_id = row[0]
        print(f"Existing survey found with ID: {survey_id}")
    else:
        # Insert new survey
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        token = str(uuid.uuid4())
        survey_link = f"http://localhost:5000/survey/fill/{token}"
        
        cur.execute(
            """
            INSERT INTO online_surveys (
                company_id, survey_title, survey_description, target_groups,
                survey_link, start_date, end_date, total_questions,
                response_count, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, "Örnek Anket 1", "Sürdürülebilirlik önceliklendirme anketi", "Employees,Customers",
             survey_link, start_date, end_date, 10, 0, 1, created_at)
        )
        survey_id = cur.lastrowid
        print(f"Created new survey with ID: {survey_id}")

        # Add some questions
        questions = [
            ("Environmental", "Karbon ayak izi azaltma hedeflerimiz yeterli mi?", "scale_1_5"),
            ("Social", "Çalışan hakları konusunda şirket performansı nasıl?", "scale_1_5"),
            ("Governance", "Şeffaflık politikamız etkin mi?", "yes_no"),
            ("General", "Genel görüşleriniz nelerdir?", "text")
        ]
        
        for idx, (cat, text, qtype) in enumerate(questions):
            cur.execute("""
                INSERT INTO survey_questions (
                    survey_id, category, question_text, question_type, 
                    is_required, display_order, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (survey_id, cat, text, qtype, 1, idx+1, created_at))

    # Check current response count
    cur.execute("SELECT COUNT(*) FROM survey_responses WHERE survey_id=?", (survey_id,))
    existing = cur.fetchone()[0]
    target = 15
    to_add = max(0, target - existing)
    
    topics = ['SDG1', 'SDG13', 'GRI_201', 'GRI_305', 'ESRS_E1']
    roles = ['Employee', 'Customer', 'Supplier', 'Investor', 'NGO']
    
    for i in range(to_add):
        idx = existing + i + 1
        name = f"Paydaş {idx}"
        email = f"paydas{idx}@example.com"
        role = random.choice(roles)
        topic = random.choice(topics)
        imp_score = random.randint(1, 5)
        impact_score = random.randint(1, 5)
        
        sql = """
            INSERT INTO survey_responses (
                survey_id, stakeholder_name, stakeholder_email, stakeholder_role, 
                topic_code, importance_score, impact_score, 
                submitted_date, comment, ip_address, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        vals = (
            survey_id, name, email, role, 
            topic, imp_score, impact_score, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
            f"Otomatik oluşturulan test yanıtı {idx}",
            "127.0.0.1", "Python Test Script"
        )
        
        cur.execute(sql, vals)
        
    cur.execute("SELECT COUNT(*) FROM survey_responses WHERE survey_id=?", (survey_id,))
    total = cur.fetchone()[0]
    
    # Update survey response count
    cur.execute(
        "UPDATE online_surveys SET response_count=? WHERE id=?",
        (total, survey_id)
    )
    
    conn.commit()
    conn.close()
    print(f"Sample survey ready. survey_id={survey_id}, responses={total}")

if __name__ == "__main__":
    db_path = get_db_path()
    create_sample_survey(db_path)
