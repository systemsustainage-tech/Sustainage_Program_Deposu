import sqlite3
import sys

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_template(template_id):
    print(f"Checking template {template_id}...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check template existence
        cursor.execute("SELECT * FROM survey_templates WHERE id=?", (template_id,))
        template = cursor.fetchone()
        if not template:
            print("Template not found.")
            return

        print(f"Template: {template['name']} (ID: {template['id']})")
        
        # Check questions
        cursor.execute("SELECT * FROM survey_template_questions WHERE template_id=?", (template_id,))
        questions = cursor.fetchall()
        print(f"Found {len(questions)} questions.")
        
        for q in questions:
            print(f"- {q['question_text']} ({q['question_type']})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_template(int(sys.argv[1]))
    else:
        print("Please provide template ID.")