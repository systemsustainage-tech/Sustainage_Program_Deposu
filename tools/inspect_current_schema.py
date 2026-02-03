import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'sdg_desktop.sqlite')

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Checking 'users' table columns:")
    cursor.execute("PRAGMA table_info(users)")
    users_columns = [row[1] for row in cursor.fetchall()]
    print(users_columns)

    tables_to_check = [
        'password_reset_tokens',
        'temp_access_tokens',
        'report_templates',
        'report_sections',
        'report_generation_log',
        'report_customizations'
    ]

    print("\nChecking existence of other tables:")
    for table in tables_to_check:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        exists = cursor.fetchone()
        print(f"{table}: {'Exists' if exists else 'MISSING'}")
        if exists:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
            print(f"  Columns: {cols}")

    conn.close()

if __name__ == "__main__":
    check_schema()
