import sqlite3
import os

db_path = 'backend/data/sdg_desktop.sqlite'
print(f"Checking DB at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='roles'")
    result = cursor.fetchone()
    if result:
        print("Schema for roles table:")
        print(result[0])
    else:
        print("Table 'roles' not found.")
except Exception as e:
    print(f"Error: {e}")

conn.close()
