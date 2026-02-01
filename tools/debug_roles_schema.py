import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'backend', 'data', 'sdg_desktop.sqlite')
print(f"Checking DB at: {db_path}")

if not os.path.exists(db_path):
    print("Database file not found!")
    exit(1)

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
