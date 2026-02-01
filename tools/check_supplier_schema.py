
import sqlite3

DB_PATH = 'c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(supplier_assessments)")
    columns = cursor.fetchall()
    print("Columns in supplier_assessments:")
    for col in columns:
        print(col)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
