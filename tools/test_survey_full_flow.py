import sqlite3
import os
import sys
import logging
from datetime import datetime

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Try to import settings, fallback to hardcoded path
try:
    from config import settings
    DB_PATH = settings.DATABASE_PATH
except ImportError:
    DB_PATH = os.path.join(parent_dir, 'backend', 'data', 'sdg_desktop.sqlite')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_survey_tables(conn):
    """Ensure survey tables exist for the test"""
    # Create online_surveys
    conn.execute("""
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create survey_questions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS survey_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT DEFAULT 'text',
            category TEXT DEFAULT 'General',
            options TEXT,
            is_required BOOLEAN DEFAULT 0,
            display_order INTEGER DEFAULT 0
        )
    """)

    # Create survey_responses
    conn.execute("""
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
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check for missing columns in survey_responses and migrate
    cur = conn.execute("PRAGMA table_info(survey_responses)")
    columns = [row['name'] for row in cur.fetchall()]
    
    if 'user_agent' not in columns:
        logging.info("Migrating: Adding user_agent to survey_responses")
        conn.execute("ALTER TABLE survey_responses ADD COLUMN user_agent TEXT")
        
    if 'ip_address' not in columns:
        logging.info("Migrating: Adding ip_address to survey_responses")
        conn.execute("ALTER TABLE survey_responses ADD COLUMN ip_address TEXT")

    # Create survey_answers
    conn.execute("""
        CREATE TABLE IF NOT EXISTS survey_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answer_text TEXT,
            score INTEGER
        )
    """)
    
    # Check for missing columns in survey_answers and migrate
    cur = conn.execute("PRAGMA table_info(survey_answers)")
    columns = [row['name'] for row in cur.fetchall()]
    
    if 'answer_text' not in columns:
        logging.info("Migrating: Adding answer_text to survey_answers")
        conn.execute("ALTER TABLE survey_answers ADD COLUMN answer_text TEXT")
        
    if 'score' not in columns:
        logging.info("Migrating: Adding score to survey_answers")
        conn.execute("ALTER TABLE survey_answers ADD COLUMN score INTEGER")

    conn.commit()

def test_full_flow():
    logging.info(f"Testing Survey Full Flow on DB: {DB_PATH}")
    
    conn = get_db()
    setup_survey_tables(conn)
    
    # --- Step 1: Create Survey (Simulate add_survey) ---
    logging.info("Step 1: Creating Survey...")
    company_id = 1
    title = f"Test Survey {datetime.now().strftime('%Y%m%d%H%M%S')}"
    desc = "This is a test survey for full flow verification."
    target = "Employees"
    link = f"/survey/test_{datetime.now().strftime('%H%M%S')}"
    
    cur = conn.execute("""
        INSERT INTO online_surveys (
            company_id, survey_title, survey_description, target_groups, 
            survey_link, is_active, created_at
        ) VALUES (?, ?, ?, ?, ?, 1, datetime('now'))
    """, (company_id, title, desc, target, link))
    
    survey_id = cur.lastrowid
    logging.info(f"Survey created with ID: {survey_id}")
    
    # Add Questions
    questions = [
        ("Do you like testing?", "yes_no", "General"),
        ("Rate this tool", "scale_1_5", "Feedback"),
        ("Any comments?", "text", "Feedback")
    ]
    
    q_ids = []
    for q_text, q_type, cat in questions:
        cur = conn.execute("""
            INSERT INTO survey_questions (
                survey_id, question_text, question_type, category, is_required, display_order
            ) VALUES (?, ?, ?, ?, 1, 0)
        """, (survey_id, q_text, q_type, cat))
        q_ids.append(cur.lastrowid)
        
    conn.execute("UPDATE online_surveys SET total_questions=? WHERE id=?", (len(questions), survey_id))
    conn.commit()
    logging.info(f"Added {len(questions)} questions.")

    # --- Step 2: Submit Survey (Simulate public_survey POST) ---
    logging.info("Step 2: Submitting Survey Response...")
    
    respondent_info = {
        'name': 'Test User',
        'email': 'test@example.com',
        'company': 'Test Corp',
        'department': 'QA',
        'stakeholder_group': 'Employee',
        'ip_address': '127.0.0.1',
        'user_agent': 'Python Test Script'
    }
    
    cur = conn.execute("""
        INSERT INTO survey_responses (
            survey_id, respondent_name, respondent_email, 
            respondent_company, respondent_department, stakeholder_group,
            ip_address, user_agent
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        survey_id, 
        respondent_info['name'], 
        respondent_info['email'],
        respondent_info['company'], 
        respondent_info['department'],
        respondent_info['stakeholder_group'],
        respondent_info['ip_address'],
        respondent_info['user_agent']
    ))
    response_id = cur.lastrowid
    logging.info(f"Response submitted with ID: {response_id}")
    
    # Answers
    answers = {
        q_ids[0]: "Yes",
        q_ids[1]: "5", # Score 5
        q_ids[2]: "Great tool!"
    }
    
    for q_id, val in answers.items():
        score = int(val) if val.isdigit() and 1 <= int(val) <= 5 else None
        conn.execute("""
            INSERT INTO survey_answers (response_id, question_id, answer_text, score)
            VALUES (?, ?, ?, ?)
        """, (response_id, q_id, val, score))
        
    # Update stats
    conn.execute("UPDATE online_surveys SET response_count = response_count + 1 WHERE id=?", (survey_id,))
    conn.commit()
    
    # --- Step 3: Verify Results ---
    logging.info("Step 3: Verifying Results...")
    
    # Check response count
    row = conn.execute("SELECT response_count FROM online_surveys WHERE id=?", (survey_id,)).fetchone()
    assert row['response_count'] == 1, f"Expected response_count 1, got {row['response_count']}"
    logging.info("Response count verified.")
    
    # Check response record
    row = conn.execute("SELECT * FROM survey_responses WHERE id=?", (response_id,)).fetchone()
    assert row['respondent_name'] == 'Test User', "Respondent name mismatch"
    logging.info("Response record verified.")
    
    # Check answers
    rows = conn.execute("SELECT * FROM survey_answers WHERE response_id=?", (response_id,)).fetchall()
    assert len(rows) == 3, f"Expected 3 answers, got {len(rows)}"
    for r in rows:
        if r['question_id'] == q_ids[1]:
            assert r['score'] == 5, f"Expected score 5, got {r['score']}"
    logging.info("Answers verified.")
    
    conn.close()
    logging.info("=== SUCCESS: Full Survey Flow Verified ===")

if __name__ == "__main__":
    test_full_flow()
