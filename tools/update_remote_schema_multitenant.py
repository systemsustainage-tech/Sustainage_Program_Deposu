import sqlite3
import os
import sys

# Define DB Path - Remote server path
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

# Global tables to exclude from company_id requirement
GLOBAL_TABLES = [
    'companies', 'users', 'roles', 'permissions', 'role_permissions',
    'user_companies', 'user_roles', 'schema_migrations', 'sqlite_sequence',
    'framework_mapping', 'sdg_goals', 'gri_standards', 'report_templates',
    'report_sections', 'languages', 'translations', 'api_endpoints',
    'api_keys', 'audit_logs', 'notifications', 'tsrs_standards',
    'supported_languages', 'company_info'
]

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        # Try local path for testing if remote path doesn't exist
        local_path = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'
        if os.path.exists(local_path):
            print(f"Using local path for testing: {local_path}")
            # BUT BE CAREFUL NOT TO RUN THIS ON LOCAL UNLESS INTENDED
            # For this script, we want to run it on REMOTE.
            # So if remote path not found, we exit.
            return

    print(f"Updating schema at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    updated_count = 0
    
    for table in tables:
        if table in GLOBAL_TABLES:
            continue
            
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'company_id' not in columns:
            print(f"Adding company_id to {table}...")
            try:
                # Add column with default value 1 (assuming primary company)
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN company_id INTEGER NOT NULL DEFAULT 1")
                updated_count += 1
            except Exception as e:
                print(f"Error updating {table}: {e}")
                
    conn.commit()
    print(f"Schema update complete. Updated {updated_count} tables.")
    
    # Verify company_targets table exists (TargetManager)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_targets'")
    if not cursor.fetchone():
        print("Creating company_targets table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                metric_type TEXT NOT NULL, -- carbon, energy, water, waste
                baseline_year INTEGER,
                baseline_value REAL,
                target_year INTEGER,
                target_value REAL,
                current_value REAL,
                status TEXT DEFAULT 'pending', -- on_track, behind, achieved, pending
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("company_targets table created.")

    conn.close()

if __name__ == "__main__":
    update_schema()
