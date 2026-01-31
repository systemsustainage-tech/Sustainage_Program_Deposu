import sqlite3
import os
import sys

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def verify():
    if not os.path.exists(DB_PATH):
        print(f"Error: DB not found at {DB_PATH}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        print(f"--- Verifying Data in {DB_PATH} ---")
        
        # Check online_surveys
        try:
            cur.execute("SELECT COUNT(*) FROM online_surveys")
            survey_count = cur.fetchone()[0]
            print(f"online_surveys count: {survey_count}")
        except Exception as e:
            print(f"Error querying online_surveys: {e}")
            survey_count = 0
        
        # Check survey_responses
        try:
            cur.execute("SELECT COUNT(*) FROM survey_responses")
            response_count = cur.fetchone()[0]
            print(f"survey_responses count: {response_count}")
        except Exception as e:
            print(f"Error querying survey_responses: {e}")
            response_count = 0
        
        if survey_count > 0 and response_count > 0:
            print("SUCCESS: Data verification passed.")
        else:
            print("WARNING: Data missing or table errors.")
            
        conn.close()
    except Exception as e:
        print(f"Error connecting to DB: {e}")

if __name__ == "__main__":
    verify()
