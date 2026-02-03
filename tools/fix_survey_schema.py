import sqlite3
import os
import sys

# Define path to database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')

def fix_schema():
    print(f"Checking schema for database: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check survey_questions table
        print("Checking survey_questions table...")
        cursor.execute("PRAGMA table_info(survey_questions)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print("Adding company_id column to survey_questions...")
            try:
                cursor.execute("ALTER TABLE survey_questions ADD COLUMN company_id INTEGER DEFAULT 1")
                print("Column added successfully.")
            except Exception as e:
                print(f"Error adding column: {e}")

        # Check online_surveys table
        print("Checking online_surveys table...")
        cursor.execute("PRAGMA table_info(online_surveys)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print("Adding company_id column to online_surveys...")
            try:
                cursor.execute("ALTER TABLE online_surveys ADD COLUMN company_id INTEGER DEFAULT 1")
                print("Column added successfully.")
            except Exception as e:
                print(f"Error adding column: {e}")
        
        if 'total_questions' not in columns:
            print("Adding total_questions column to online_surveys...")
            try:
                cursor.execute("ALTER TABLE online_surveys ADD COLUMN total_questions INTEGER DEFAULT 0")
                print("Column added successfully.")
            except Exception as e:
                print(f"Error adding column: {e}")

        # Check survey_responses table
        print("Checking survey_responses table...")
        cursor.execute("PRAGMA table_info(survey_responses)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print("Adding company_id column to survey_responses...")
            try:
                cursor.execute("ALTER TABLE survey_responses ADD COLUMN company_id INTEGER DEFAULT 1")
                print("Column added successfully.")
            except Exception as e:
                print(f"Error adding column: {e}")

        # Check survey_answers table
        print("Checking survey_answers table...")
        cursor.execute("PRAGMA table_info(survey_answers)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print("Adding company_id column to survey_answers...")
            try:
                cursor.execute("ALTER TABLE survey_answers ADD COLUMN company_id INTEGER DEFAULT 1")
                print("Column added successfully.")
            except Exception as e:
                print(f"Error adding column: {e}")
            
        conn.commit()
        conn.close()
        print("Schema check completed.")
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    fix_schema()
