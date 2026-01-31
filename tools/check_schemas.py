import sqlite3
import os

DB_PATH = '/var/www/sustainage/sustainage.db'

def check_schemas():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("--- Schema Check ---")
        
        # Check survey_questions
        try:
            cursor.execute("PRAGMA table_info(survey_questions)")
            cols = [row[1] for row in cursor.fetchall()]
            print(f"survey_questions columns: {cols}")
        except Exception as e:
            print(f"Error checking survey_questions: {e}")
            
        # Check map_sdg_gri
        try:
            cursor.execute("PRAGMA table_info(map_sdg_gri)")
            cols = [row[1] for row in cursor.fetchall()]
            print(f"map_sdg_gri columns: {cols}")
            if 'relation_type' in cols:
                print("SUCCESS: map_sdg_gri has 'relation_type'.")
            else:
                print("FAILURE: map_sdg_gri MISSING 'relation_type'.")
        except Exception as e:
            print(f"Error checking map_sdg_gri: {e}")
            
        conn.close()
    except Exception as e:
        print(f"Error connecting to DB: {e}")

if __name__ == "__main__":
    check_schemas()
