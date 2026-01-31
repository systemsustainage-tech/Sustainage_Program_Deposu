import sqlite3
import os
import sys

# Hardcoded DB path for simplicity on remote
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def diagnose():
    print(f"Diagnosing DB at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n--- Recent Surveys (Last 5) ---")
    try:
        cursor.execute("SELECT id, survey_title, created_at, total_questions FROM online_surveys ORDER BY id DESC LIMIT 5")
        surveys = cursor.fetchall()
        for s in surveys:
            # Count actual questions in table
            try:
                q_count = conn.execute("SELECT count(*) FROM survey_questions WHERE survey_id=?", (s['id'],)).fetchone()[0]
            except Exception as e:
                q_count = f"Error: {e}"
            print(f"ID: {s['id']}, Title: {s['survey_title']}, Created: {s['created_at']}, Metadata Count: {s['total_questions']}, Actual Count: {q_count}")
    except Exception as e:
        print(f"Error reading online_surveys: {e}")
        
    print("\n--- Survey Templates ---")
    try:
        cursor.execute("SELECT id, name FROM survey_templates")
        templates = cursor.fetchall()
        for t in templates:
            try:
                q_count = conn.execute("SELECT count(*) FROM survey_template_questions WHERE template_id=?", (t['id'],)).fetchone()[0]
            except Exception as e:
                q_count = f"Error: {e}"
            print(f"ID: {t['id']}, Name: {t['name']}, Question Count: {q_count}")
            
        print("\n--- Sample Template Questions (First 3) ---")
        if templates:
            cursor.execute("SELECT * FROM survey_template_questions WHERE template_id=? LIMIT 3", (templates[0]['id'],))
            qs = cursor.fetchall()
            for q in qs:
                print(dict(q))
    except Exception as e:
        print(f"Error reading templates: {e}")
            
    conn.close()

if __name__ == "__main__":
    diagnose()
