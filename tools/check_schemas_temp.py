import sqlite3
import os

# DB_PATH = os.path.join(os.getcwd(), 'sustainage.db')
DB_PATH = os.path.join(os.getcwd(), 'backend', 'data', 'sdg_desktop.sqlite')

print(f"Checking DB: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tables = ['surveys', 'online_surveys', 'survey_responses', 'survey_questions']

for table in tables:
    print(f"\n--- {table} ---")
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        rows = cursor.fetchall()
        if not rows:
            print("Table does not exist.")
        else:
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error: {e}")

# Check content count
for table in tables:
    print(f"\nCount {table}:")
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(cursor.fetchone()[0])
    except:
        print("Error/Table missing")

conn.close()
