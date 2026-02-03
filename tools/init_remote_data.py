import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def init_data():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if companies exist
    try:
        cursor.execute("SELECT count(*) FROM companies")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Inserting default company...")
            cursor.execute("INSERT INTO companies (name, sector, employee_count) VALUES (?, ?, ?)", 
                           ('Demo Company', 'Technology', 100))
            company_id = cursor.lastrowid
            conn.commit()
            print(f"Company created with ID {company_id}")
        else:
            print(f"Found {count} companies.")
            cursor.execute("SELECT id FROM companies LIMIT 1")
            company_id = cursor.fetchone()[0]
            print(f"Using company ID {company_id}")
            
    except Exception as e:
        print(f"Error: {e}")
        
    conn.close()

if __name__ == "__main__":
    init_data()
