
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def verify_sdg_data():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check Tables
        tables = ['sdg_goals', 'sdg_targets', 'sdg_indicators', 'sdg_responses', 'user_sdg_selections']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"[OK] Table '{table}' exists. Count: {count}")
            except sqlite3.OperationalError as e:
                print(f"[FAIL] Table '{table}' error: {e}")

        # Check Specific Data
        cursor.execute("SELECT code, title_tr FROM sdg_goals LIMIT 1")
        goal = cursor.fetchone()
        if goal:
            print(f"[INFO] Sample Goal: {goal}")
        
        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_sdg_data()
