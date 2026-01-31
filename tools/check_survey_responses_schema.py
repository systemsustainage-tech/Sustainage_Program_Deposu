import sqlite3
import os

DB_PATH = 'backend/data/sdg_desktop.sqlite'

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    tables = ['survey_questions', 'survey_responses', 'survey_answers']
    
    for table in tables:
        print(f"\n--- Schema for {table} ---")
        try:
            cur.execute(f"PRAGMA table_info({table})")
            rows = cur.fetchall()
            if not rows:
                print(f"Table {table} does not exist.")
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    check_schema()
