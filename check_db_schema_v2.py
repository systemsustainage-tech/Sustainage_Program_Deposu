import sqlite3
import os

db_path = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
print(f"Checking database at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(sdg_indicators)")
    columns = cursor.fetchall()
    print("Columns in sdg_indicators:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
