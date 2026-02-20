import sqlite3
import os

db_path = 'sustainage.db'
if not os.path.exists(db_path):
    print("Database not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'investment%'")
    tables = cursor.fetchall()
    print("Found tables:", tables)
    
    # Check columns for investment_projects if it exists
    if any(t[0] == 'investment_projects' for t in tables):
        cursor.execute("PRAGMA table_info(investment_projects)")
        columns = cursor.fetchall()
        print("\nColumns in investment_projects:")
        for col in columns:
            print(col)
            
    conn.close()
