import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def verify_schema():
    print(f"Checking schema for database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        tables = ['survey_questions', 'online_surveys', 'survey_responses', 'survey_answers']
        
        for table in tables:
            print(f"Checking {table} table...")
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [info[1] for info in cursor.fetchall()]
                
                if 'company_id' in columns:
                    print(f"  [OK] company_id exists in {table}")
                else:
                    print(f"  [FAIL] company_id MISSING in {table}")
                    
                if table == 'online_surveys':
                    if 'total_questions' in columns:
                         print(f"  [OK] total_questions exists in {table}")
                    else:
                         print(f"  [FAIL] total_questions MISSING in {table}")

            except Exception as e:
                print(f"  Error checking {table}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    verify_schema()
