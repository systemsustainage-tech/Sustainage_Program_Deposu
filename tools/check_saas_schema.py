import sqlite3
import os
import sys

# Add backend to path to allow importing config if needed (though we use direct DB path here)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, '..', 'backend')
DB_PATH = os.path.join(BACKEND_DIR, 'data', 'sdg_desktop.sqlite')

def check_schema():
    print(f"Checking database at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    missing_company_id = []
    safe_tables = ['sqlite_sequence', 'alembic_version'] # System tables to ignore
    
    # Tables that naturally don't need company_id (e.g., global configs, users table itself maybe?)
    # Users table needs careful checking, but typically users belong to companies or are linked.
    # For now, let's just list everything.
    global_tables = ['users', 'roles', 'permissions', 'user_roles', 'companies', 'company_info'] 
    # 'companies' obviously doesn't need company_id (it IS the company definition)
    # 'users' might need it if strict 1-1, but usually many-to-many via user_companies
    
    print("\n--- Scanning Tables for 'company_id' column ---")
    
    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        if table_name in safe_tables:
            continue
            
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'company_id' not in column_names:
            if table_name not in global_tables:
                missing_company_id.append(table_name)
                print(f"[WARNING] Table '{table_name}' is missing 'company_id'")
            else:
                print(f"[INFO] Global Table '{table_name}' does not have 'company_id' (Expected)")
        else:
            # print(f"[OK] Table '{table_name}' has 'company_id'")
            pass

    print("\n--- Summary ---")
    if missing_company_id:
        print(f"Found {len(missing_company_id)} tables missing 'company_id' that might need it.")
        print("List:", missing_company_id)
    else:
        print("All relevant tables seem to have 'company_id'. Schema is SaaS-ready!")

    conn.close()

if __name__ == "__main__":
    check_schema()
