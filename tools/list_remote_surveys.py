import sqlite3
import os

DB_PATH = '/var/www/sustainage/sustainage.db'

def list_surveys():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, survey_title, survey_link, is_active FROM online_surveys")
        surveys = cursor.fetchall()
        
        if not surveys:
            print("No surveys found.")
        else:
            print("Found surveys:")
            for s in surveys:
                print(f"ID: {s[0]}, Title: {s[1]}, Link: {s[2]}, Active: {s[3]}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_surveys()
