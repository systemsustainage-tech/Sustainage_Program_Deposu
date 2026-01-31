import sqlite3
import os

db_path = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("--- Templates ---")
    try:
        cursor.execute("SELECT id, name FROM survey_templates")
        for row in cursor.fetchall():
            print(row)
    except Exception as e:
        print(f"Table survey_templates error: {e}")

    print("\n--- Questions Count ---")
    try:
        cursor.execute("SELECT COUNT(*) FROM survey_template_questions")
        print(cursor.fetchone()[0])
    except Exception as e:
        print(f"Table survey_template_questions error: {e}")
except Exception as e:
    print(f"Error: {e}")

conn.close()
