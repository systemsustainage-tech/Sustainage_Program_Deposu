import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'sdg_desktop.sqlite')

def check_surveys():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        print("Checking online_surveys table...")
        cursor = conn.execute("SELECT * FROM online_surveys")
        rows = cursor.fetchall()
        if not rows:
            print("No surveys found in online_surveys.")
        else:
            print(f"Found {len(rows)} surveys:")
            print(f"Columns: {rows[0].keys()}")
            for row in rows:
                row = dict(row)
                print(f"ID: {row.get('id')}, Title: {row.get('survey_title')}, Link: {row.get('survey_link')}, Active: {row.get('is_active')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_surveys()
