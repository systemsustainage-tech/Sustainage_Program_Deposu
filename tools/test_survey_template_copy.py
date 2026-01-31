import sqlite3
import sys
import datetime

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def test_template_copy(template_id):
    print(f"Testing template copy for template_id: {template_id}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Create a test survey
        print("Creating test survey...")
        cursor.execute("""
            INSERT INTO online_surveys (
                company_id, survey_title, survey_description, target_groups, 
                survey_link, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, 1, datetime('now'))
        """, (1, f"Test Survey Template {template_id}", "Test Description", "Test Group", f"/survey/test_template_{template_id}_{int(datetime.datetime.now().timestamp())}"))
        
        survey_id = cursor.lastrowid
        print(f"Created survey ID: {survey_id}")
        
        # 2. Simulate the copy logic from web_app.py
        print("Copying questions...")
        t_cursor = conn.execute("SELECT * FROM survey_template_questions WHERE template_id=?", (template_id,))
        t_questions = t_cursor.fetchall()
        
        print(f"Found {len(t_questions)} questions in template.")
        
        for tq in t_questions:
            q = dict(tq)
            conn.execute("""
                INSERT INTO survey_questions (
                    survey_id, question_text, question_type, 
                    category, options, is_required, display_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                survey_id, q['question_text'], q['question_type'],
                q.get('category', 'General'), q.get('options'), 
                1, 0
            ))
            
        # Update question count
        conn.execute("UPDATE online_surveys SET total_questions=? WHERE id=?", (len(t_questions), survey_id))
        conn.commit()
        
        # 3. Verify
        print("Verifying copy...")
        q_count = conn.execute("SELECT count(*) FROM survey_questions WHERE survey_id=?", (survey_id,)).fetchone()[0]
        print(f"Survey {survey_id} has {q_count} questions.")
        
        if q_count == len(t_questions) and q_count > 0:
            print("SUCCESS: Questions copied correctly.")
        else:
            print("FAILURE: Question count mismatch or zero.")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_template_copy(int(sys.argv[1]))
    else:
        print("Please provide template ID")