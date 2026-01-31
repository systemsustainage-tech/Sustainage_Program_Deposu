
import sqlite3
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from config.database import DB_PATH

def check_data():
    print(f"Checking DB at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n--- SDG Indicators (ID=1) ---")
    try:
        cursor.execute("SELECT * FROM sdg_indicators WHERE id=1")
        row = cursor.fetchone()
        if row:
            print(dict(row))
        else:
            print("Indicator ID 1 NOT FOUND")
            
        cursor.execute("SELECT COUNT(*) FROM sdg_indicators")
        print(f"Total indicators: {cursor.fetchone()[0]}")
    except Exception as e:
        print(f"Error checking SDG indicators: {e}")

    print("\n--- SDG Responses ---")
    try:
        cursor.execute("SELECT * FROM responses ORDER BY created_at DESC LIMIT 5")
        rows = cursor.fetchall()
        if not rows:
            print("No responses found.")
        for row in rows:
            print(dict(row))
    except Exception as e:
        print(f"Error checking SDG responses: {e}")

    print("\n--- Companies ---")
    try:
        cursor.execute("SELECT * FROM companies")
        rows = cursor.fetchall()
        if not rows:
            print("No companies found.")
        for row in rows:
            print(dict(row))
    except Exception as e:
        print(f"Error checking companies: {e}")

    print("\n--- CSRD Assessments ---")
    try:
        cursor.execute("SELECT * FROM double_materiality_assessment ORDER BY created_at DESC LIMIT 5")
        for row in cursor.fetchall():
            print(dict(row))
    except Exception as e:
        print(f"Error checking CSRD assessments: {e}")

    print("\n--- IIRC Reports ---")
    try:
        cursor.execute("SELECT * FROM integrated_reports ORDER BY created_at DESC LIMIT 5")
        for row in cursor.fetchall():
            print(dict(row))
    except Exception as e:
        print(f"Error checking IIRC reports: {e}")

    conn.close()

if __name__ == "__main__":
    check_data()
