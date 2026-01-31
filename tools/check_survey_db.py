
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        print(f"--- Checking online_surveys in {DB_PATH} ---")
        cur.execute("SELECT id, survey_title, survey_link, is_active, company_id FROM online_surveys")
        rows = cur.fetchall()
        if not rows:
            print("No surveys found.")
        for row in rows:
            print(dict(row))
            
        print("\n--- Checking survey_questions ---")
        cur.execute("SELECT id, survey_id, question_text FROM survey_questions LIMIT 5")
        rows = cur.fetchall()
        for row in rows:
            print(dict(row))
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
