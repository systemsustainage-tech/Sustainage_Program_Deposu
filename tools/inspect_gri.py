import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sustainage.db')

def check_gri():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gri_standards'")
        if not cursor.fetchone():
            print("gri_standards table does NOT exist.")
            return

        # Check column names
        cursor.execute("PRAGMA table_info(gri_standards)")
        columns = cursor.fetchall()
        print("Columns:", [col[1] for col in columns])

        # Check for sector specific standards (e.g., GRI 11, GRI 12, GRI 13)
        cursor.execute("SELECT DISTINCT code, title FROM gri_standards WHERE code LIKE 'GRI 1%' OR code LIKE 'GRI 2%' ORDER BY code")
        standards = cursor.fetchall()
        print("\nFound Standards (Sample):")
        for s in standards:
            print(f"- {s[0]}: {s[1]}")

        # Check total count
        cursor.execute("SELECT COUNT(*) FROM gri_standards")
        count = cursor.fetchone()[0]
        print(f"\nTotal GRI Standards rows: {count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_gri()
