import sqlite3
import os
import sys

# Add parent directory to path to import config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def audit_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    tables_missing_company_id = []
    tables_with_company_id = []
    
    print(f"Scanning {len(tables)} tables for 'company_id' column...\n")
    
    # Exclude system tables or tables that are global by design
    GLOBAL_TABLES = [
        'companies', # The master list of companies
        'users',     # Users might belong to multiple companies (handled by user_companies)
        'roles',     # Global roles
        'permissions', # Global permissions
        'role_permissions',
        'user_companies', # The link table
        'user_roles',
        'schema_migrations',
        'sqlite_sequence',
        'framework_mapping', # Static data
        'sdg_goals', # Static data
        'gri_standards', # Static data
        'report_templates', # Could be global or tenant specific? Let's check.
        'report_sections', # Linked to template
        'languages', # Global
        'translations', # Global
        'api_endpoints', # Global or Tenant? Check schema.
        'api_keys',      # Global or Tenant? Check schema.
        'audit_logs',    # Might need company_id but often global for system admins
        'notifications', # Notifications might be user-specific, but checking... usually has user_id
        'tsrs_standards', # Global standards catalog
        'supported_languages', # Global platform languages
    ]

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'company_id' in columns:
            tables_with_company_id.append(table)
        else:
            if table not in GLOBAL_TABLES:
                tables_missing_company_id.append(table)
    
    print(f"Tables WITH company_id ({len(tables_with_company_id)}):")
    for t in tables_with_company_id:
        print(f"  - {t}")
        
    print(f"\nTables MISSING company_id ({len(tables_missing_company_id)}):")
    for t in tables_missing_company_id:
        print(f"  - {t}")
        
    conn.close()

if __name__ == "__main__":
    audit_schema()
