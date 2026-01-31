
import sqlite3
import os

db_path = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"
print(f"Checking DB: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table info
    print("Table Info:")
    cursor.execute("PRAGMA table_info(sdg_indicators)")
    cols = cursor.fetchall()
    for c in cols:
        print(c)
        
    # Check query
    print("\nExecuting Query:")
    cursor.execute("SELECT id, code, title_tr, unit, measurement_frequency as frequency, topic FROM sdg_indicators LIMIT 1")
    row = cursor.fetchone()
    print("Row:", row)
    
    conn.close()
    print("Success")
except Exception as e:
    print(f"Error: {e}")
