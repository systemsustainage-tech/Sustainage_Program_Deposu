import sqlite3
import os

db_path = r'C:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def print_schema(table_name):
    print(f"--- Schema for {table_name} ---")
    try:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        row = cursor.fetchone()
        if row:
            print(row[0])
        else:
            print(f"Table {table_name} does not exist.")
    except Exception as e:
        print(f"Error: {e}")

print_schema('licenses')
print_schema('companies')
conn.close()
