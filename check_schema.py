import sqlite3
try:
    conn = sqlite3.connect('c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN ('carbon_emissions', 'waste_generation', 'energy_consumption', 'water_consumption')")
    for row in cursor.fetchall():
        print(f"--- {row[0]} ---")
        print(row[1])
        print()
    conn.close()
except Exception as e:
    print(e)
