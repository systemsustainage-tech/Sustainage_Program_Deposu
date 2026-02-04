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
    
    print(f"--- Assigning Company to Admin (ID: 1) in {DB_PATH} ---")
    
    # 1. Get a company
    cursor.execute("SELECT id FROM companies ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    if not row:
        print("No companies found! Creating default company...")
        cursor.execute("INSERT INTO companies (name, sector, country) VALUES ('Default Company', 'Technology', 'Turkey')")
        company_id = cursor.lastrowid
        print(f"Created company with ID: {company_id}")
    else:
        company_id = row[0]
        print(f"Found existing company ID: {company_id}")
        
    # 2. Assign to admin
    # Check if already assigned
    cursor.execute("SELECT 1 FROM user_companies WHERE user_id=1 AND company_id=?", (company_id,))
    if cursor.fetchone():
        print("Admin is already assigned to this company.")
        # Ensure it is primary
        cursor.execute("UPDATE user_companies SET is_primary=1 WHERE user_id=1 AND company_id=?", (company_id,))
        print("Ensured it is primary.")
    else:
        print(f"Assigning Admin to Company {company_id}...")
        cursor.execute("INSERT INTO user_companies (user_id, company_id, is_primary) VALUES (1, ?, 1)", (company_id,))
        print("Assignment successful.")
        
    conn.commit()
    conn.close()
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
