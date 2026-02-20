import sqlite3
import os

db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(report_templates)")
    columns = cursor.fetchall()
    print("report_templates columns:")
    for col in columns:
        print(col)
except Exception as e:
    print(f"Error: {e}")

conn.close()
