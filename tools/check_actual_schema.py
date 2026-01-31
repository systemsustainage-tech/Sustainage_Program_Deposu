
import sqlite3
import os

if os.name == 'nt':
    db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
else:
    db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def print_schema(table_name):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print(f"--- Schema for {table_name} ---")
    try:
        cur.execute(f"PRAGMA table_info({table_name})")
        rows = cur.fetchall()
        if not rows:
            print(f"Table {table_name} does not exist.")
        else:
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error: {e}")
    conn.close()

if __name__ == "__main__":
    print_schema("online_surveys")
    print_schema("surveys")
    print_schema("survey_responses")
    print_schema("survey_questions")
