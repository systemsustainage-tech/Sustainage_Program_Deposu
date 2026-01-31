import sqlite3
import os

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def inspect():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        print("--- survey_questions ---")
        try:
            cur.execute("PRAGMA table_info(survey_questions)")
            for row in cur.fetchall():
                print(row)
            
            print("\n--- Sample data from survey_questions ---")
            cur.execute("SELECT * FROM survey_questions LIMIT 5")
            for row in cur.fetchall():
                print(row)
        except Exception as e:
            print(f"Error reading survey_questions: {e}")
            
        conn.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    inspect()
