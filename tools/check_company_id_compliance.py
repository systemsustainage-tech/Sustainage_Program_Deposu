import sqlite3
import os
import sys

# Define DB Path
if os.name == 'nt':
    DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
else:
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

# Tables that are inherently global or system-related and should NOT be tenant-scoped
GLOBAL_TABLES = {
    # System tables
    'sqlite_sequence',
    'schema_migrations',
    'alembic_version',
    
    # Core Multi-tenant tables
    'companies',        # The tenants themselves
    'user_companies',   # Link table
    'users',            # Users are global entities (can belong to multiple companies)
    'roles',            # Global roles definition
    'permissions',      # Global permissions definition
    'role_permissions', # Global role-permission links
    'user_roles',       # User-role assignments (could be per company, but table structure usually global with company_id link? If it's a link table, it might need company_id. Assuming global for now or handled via user_companies)
    
    # Static/System Data
    'languages',
    'translations',
    'translation_dictionary',
    'system_settings',  # Usually global settings for the app
    'framework_mapping',
    'sdg_goals',
    'gri_standards',
    'report_templates', # Templates might be global, cloned to tenants? Assuming global templates.
    'report_sections',
    'api_endpoints',    # System definition
    'api_keys',         # System definition (or could be tenant? Let's assume tenant, but check if missing)
}

def check_compliance():
    print(f"Checking database compliance at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]

    missing_company_id = []
    compliant_tables = []
    global_ignored = []

    print(f"\nScanning {len(tables)} tables...")
    print("-" * 50)

    for table in tables:
        if table in GLOBAL_TABLES:
            global_ignored.append(table)
            continue

        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]

        if 'company_id' in columns:
            compliant_tables.append(table)
        else:
            missing_company_id.append(table)

    # Report
    print(f"✅ Compliant Tables ({len(compliant_tables)}):")
    # for t in compliant_tables: print(f"  - {t}") # Too verbose?

    print(f"\n🌍 Global/Ignored Tables ({len(global_ignored)}):")
    for t in global_ignored:
        print(f"  - {t}")

    print(f"\n❌ Tables MISSING 'company_id' ({len(missing_company_id)}):")
    if missing_company_id:
        for t in missing_company_id:
            print(f"  - {t}")
        
        print("\n[SUGGESTED ACTION] Run the following SQL to fix (Backup first!):")
        print("-" * 50)
        for t in missing_company_id:
            print(f"ALTER TABLE {t} ADD COLUMN company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE;")
            print(f"-- Note: You may need to populate company_id for existing rows: UPDATE {t} SET company_id = 1 WHERE company_id IS NULL;")
        print("-" * 50)
    else:
        print("\n🎉 All tenant-specific tables have 'company_id' column!")

    conn.close()

if __name__ == "__main__":
    check_compliance()
