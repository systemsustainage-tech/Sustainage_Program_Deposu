import sqlite3
import os
import sys

# Try multiple possible paths for the DB
possible_paths = [
    'backend/data/sdg_desktop.sqlite',
    '../backend/data/sdg_desktop.sqlite',
    r'C:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
]

db_path = None
for p in possible_paths:
    if os.path.exists(p):
        db_path = p
        break

if not db_path:
    print("Database file not found in any known location!")
    print(f"CWD: {os.getcwd()}")
    sys.exit(1)

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
