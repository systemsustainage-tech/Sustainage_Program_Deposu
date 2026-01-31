import sqlite3

db_path = "c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- system_settings info ---")
cursor.execute("PRAGMA table_info(system_settings)")
for col in cursor.fetchall():
    print(col)

print("\n--- sdg_goals info ---")
cursor.execute("PRAGMA table_info(sdg_goals)")
for col in cursor.fetchall():
    print(col)

conn.close()
