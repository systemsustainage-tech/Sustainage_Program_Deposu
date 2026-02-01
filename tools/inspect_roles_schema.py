import sqlite3

db_path = 'backend/data/sdg_desktop.sqlite'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='roles'")
schema = cursor.fetchone()[0]
print(schema)

conn.close()
