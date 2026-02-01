import sqlite3
import os
import sys

# Hardcoded for remote execution
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Fixing schema...")
    
    # 1. employee_satisfaction
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employee_satisfaction'")
        if cursor.fetchone():
            print("Checking employee_satisfaction...")
            cursor.execute("PRAGMA table_info(employee_satisfaction)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'satisfaction_score' not in columns:
                print("Adding satisfaction_score to employee_satisfaction")
                cursor.execute("ALTER TABLE employee_satisfaction ADD COLUMN satisfaction_score REAL")
            
            if 'year' not in columns:
                print("Adding year to employee_satisfaction")
                cursor.execute("ALTER TABLE employee_satisfaction ADD COLUMN year INTEGER")
    except Exception as e:
        print(f"Error fixing employee_satisfaction: {e}")

    # 2. csrd_records
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='csrd_records'")
        if cursor.fetchone():
            print("Checking csrd_records...")
            cursor.execute("PRAGMA table_info(csrd_records)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'created_at' not in columns:
                print("Adding created_at to csrd_records")
                cursor.execute("ALTER TABLE csrd_records ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
    except Exception as e:
        print(f"Error fixing csrd_records: {e}")

    # 3. stakeholder_surveys
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stakeholder_surveys'")
        if cursor.fetchone():
            print("Checking stakeholder_surveys...")
            cursor.execute("PRAGMA table_info(stakeholder_surveys)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'stakeholder_group' not in columns:
                 print("Adding stakeholder_group to stakeholder_surveys")
                 cursor.execute("ALTER TABLE stakeholder_surveys ADD COLUMN stakeholder_group TEXT")
    except Exception as e:
        print(f"Error fixing stakeholder_surveys: {e}")

    conn.commit()
    conn.close()
    print("Schema fix completed.")

if __name__ == "__main__":
    fix_schema()
