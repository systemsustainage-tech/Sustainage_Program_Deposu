import sqlite3
import os

db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(table[0])
conn.close()
