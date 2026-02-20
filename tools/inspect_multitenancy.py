import sqlite3
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data', 'sdg_desktop.sqlite')

def inspect_tables():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    
    tables_missing_company_id = []
    tables_with_company_id = []
    
    # Exclude system tables or specific global tables
    EXCLUDE_TABLES = ['sqlite_sequence', 'alembic_version', 'companies', 'users', 'roles', 'permissions', 'role_permissions', 'audit_logs']
    # 'users' usually has company_id, but it's a shared table. 'companies' is the source.
    
    print(f"Inspecting {len(tables)} tables...")
    
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cur.fetchall()]
        
        if 'company_id' in columns:
            tables_with_company_id.append(table)
        else:
            if table not in EXCLUDE_TABLES:
                tables_missing_company_id.append(table)

    print(f"\nTables with company_id ({len(tables_with_company_id)}):")
    print(", ".join(tables_with_company_id))
    
    print(f"\nTables MISSING company_id ({len(tables_missing_company_id)}):")
    for t in tables_missing_company_id:
        print(f"- {t}")

    conn.close()

if __name__ == "__main__":
    inspect_tables()
