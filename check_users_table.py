import sqlite3
import os

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

if not os.path.exists(DB_PATH):
    print(f"DB not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
rows = cursor.fetchall()
print(f"Users table exists: {bool(rows)}")
conn.close()
