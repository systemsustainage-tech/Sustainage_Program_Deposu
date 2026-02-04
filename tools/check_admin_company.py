import sqlite3
import sys
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
if not os.path.exists(DB_PATH):
    # Fallback for local testing
    DB_PATH = 'c:/SUSTAINAGESERVER/backend/data/sdg_desktop.sqlite'

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"--- Checking User Companies for Admin (ID: 1) in {DB_PATH} ---")
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_companies'")
    if not cursor.fetchone():
        print("ERROR: user_companies table does not exist!")
        sys.exit(1)

    cursor.execute("SELECT * FROM user_companies WHERE user_id=1")
    rows = cursor.fetchall()
    if rows:
        print("Found companies for admin:")
        for row in rows:
            print(row)
    else:
        print("NO COMPANIES FOUND for Admin!")
        
    # Also check if companies table has any company
    cursor.execute("SELECT id, name FROM companies")
    comps = cursor.fetchall()
    print("\n--- Available Companies ---")
    for c in comps:
        print(c)
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
