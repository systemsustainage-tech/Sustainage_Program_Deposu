
import sqlite3

db_path = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- surveys ---")
cur.execute("PRAGMA table_info(surveys)")
for row in cur.fetchall():
    print(row)

print("\n--- survey_questions ---")
cur.execute("PRAGMA table_info(survey_questions)")
for row in cur.fetchall():
    print(row)

print("\n--- survey_responses ---")
cur.execute("PRAGMA table_info(survey_responses)")
for row in cur.fetchall():
    print(row)

conn.close()
