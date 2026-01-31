import sys
import os
sys.path.insert(0, '/var/www/sustainage')
from web_app import get_db

try:
    print("Testing web_app.get_db() connection...")
    conn = get_db()
    cursor = conn.cursor()
    
    # Check database file path if possible (sqlite specific)
    cursor.execute("PRAGMA database_list")
    dbs = cursor.fetchall()
    for db in dbs:
        print(f"Database attached: {db[2]}")

    print("Executing query on sdg_indicators...")
    cursor.execute("SELECT id, code, title_tr, unit, measurement_frequency as frequency FROM sdg_indicators LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"Row found: id={row['id']}, unit={row['unit']}")
    else:
        print("Table empty but query executed.")
        
    print("SUCCESS: unit column found via web_app.get_db()")
except Exception as e:
    print(f"ERROR: {e}")
