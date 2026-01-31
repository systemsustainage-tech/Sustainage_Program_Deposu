
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_survey_questions():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Check if template_id exists
        cur.execute("PRAGMA table_info(survey_questions)")
        columns = [row[1] for row in cur.fetchall()]
        
        if 'template_id' not in columns:
            print("Adding template_id to survey_questions...")
            cur.execute("ALTER TABLE survey_questions ADD COLUMN template_id INTEGER")
            conn.commit()
            print("Done.")
        else:
            print("template_id already exists in survey_questions.")

        if 'weight' not in columns:
            print("Adding weight to survey_questions...")
            cur.execute("ALTER TABLE survey_questions ADD COLUMN weight REAL DEFAULT 1.0")
            conn.commit()
            print("Done.")
        else:
            print("weight already exists in survey_questions.")

        if 'sdg_mapping' not in columns:
            print("Adding sdg_mapping to survey_questions...")
            cur.execute("ALTER TABLE survey_questions ADD COLUMN sdg_mapping TEXT")
            conn.commit()
            print("Done.")
        else:
            print("sdg_mapping already exists in survey_questions.")
            
        conn.close()
    except Exception as e:
        print(f"Error fixing survey_questions: {e}")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
    else:
        fix_survey_questions()
