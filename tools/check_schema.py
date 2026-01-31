import sqlite3
import os

db_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(gri_standards)")
    columns = cursor.fetchall()
    print("Columns in gri_standards:")
    for col in columns:
        print(col)
    conn.close()
