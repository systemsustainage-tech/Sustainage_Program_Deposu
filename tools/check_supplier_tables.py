import sqlite3

DB_PATH = 'c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'supplier%'")
    tables = cursor.fetchall()
    print("Found supplier tables:", tables)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
