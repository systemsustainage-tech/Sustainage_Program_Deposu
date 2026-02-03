
import sqlite3
import os

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = [
        'employee_satisfaction',
        'training_records',
        'ohs_incidents',
        'human_rights_assessments',
        'fair_labor_audits',
        'scope1_emissions',
        'scope2_emissions',
        'scope3_emissions'
    ]
    
    print(f"Checking DB: {DB_PATH}")
    print("--- Table Counts ---")
    for table in tables:
        try:
            # Check if table exists first
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"{table}: TABLE NOT FOUND")
                continue

            cursor.execute(f"SELECT company_id, COUNT(*) FROM {table} GROUP BY company_id")
            rows = cursor.fetchall()
            if rows:
                print(f"  [OK] Data found in '{table}'. Distribution by company_id: {rows}")
                # Check for date columns
                if 'emissions' in table:
                    cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE invoice_date IS NOT NULL AND invoice_date != ''")
                    date_count = cursor.fetchone()[0]
                    print(f"       Records with invoice_date: {date_count} / {sum(r[1] for r in rows)}")
            else:
                print(f"  [WARN] Table '{table}' exists but is EMPTY.")
        except Exception as e:
            print(f"{table}: Error - {e}")

    conn.close()

if __name__ == "__main__":
    check_db()
