import sqlite3
import os

db_path = 'backend/sustainage.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("PRAGMA table_info(gri_standards)")
    columns = cursor.fetchall()
    print("Columns in gri_standards:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
