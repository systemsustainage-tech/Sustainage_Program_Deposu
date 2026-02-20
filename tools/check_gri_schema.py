import sqlite3
import os

db_path = 'c:/SUSTAINAGESERVER/backend/sustainage.db'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = ['gri_standards', 'gri_indicators']
for table in tables:
    print(f"--- {table} ---")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
conn.close()
