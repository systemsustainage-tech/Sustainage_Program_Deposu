
import sys
import os
import sqlite3

# Set up paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from web_app import DB_PATH
except:
    DB_PATH = os.path.join(parent_dir, 'backend', 'data', 'sdg_desktop.sqlite')

print(f"DB Path: {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("-" * 30)
    print("Schema for survey_questions:")
    cursor.execute("PRAGMA table_info(survey_questions)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
        
    print("-" * 30)
    print("Schema for online_surveys:")
    cursor.execute("PRAGMA table_info(online_surveys)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)

    conn.close()
except Exception as e:
    print(f"Error inspecting DB: {e}")
