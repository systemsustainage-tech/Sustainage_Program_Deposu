import sqlite3
import os
import sys

DB_PATH = "/var/www/sustainage/data/sdg_desktop.sqlite"

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return False
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("Connected to DB.")
    
    # 1. Check carbon_emissions
    print("\nChecking carbon_emissions...")
    cursor.execute("PRAGMA table_info(carbon_emissions)")
    columns = [row['name'] for row in cursor.fetchall()]
    print(f"Existing columns: {columns}")
    
    if 'source' not in columns:
        print("Adding 'source' column...")
        try:
            cursor.execute("ALTER TABLE carbon_emissions ADD COLUMN source TEXT")
            print("Added 'source'.")
        except Exception as e:
            print(f"Error adding 'source': {e}")
            
    # 2. Check carbon_targets
    print("\nChecking carbon_targets...")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='carbon_targets'")
        if not cursor.fetchone():
            print("Creating carbon_targets table...")
            cursor.execute("""
                CREATE TABLE carbon_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    target_name TEXT,
                    target_description TEXT,
                    scope_coverage TEXT,
                    baseline_year TEXT,
                    baseline_co2e REAL,
                    target_year TEXT,
                    target_co2e REAL,
                    target_reduction_pct REAL,
                    target_type TEXT,
                    sbti_approved BOOLEAN,
                    status TEXT,
                    progress_pct REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created carbon_targets.")
        else:
            cursor.execute("PRAGMA table_info(carbon_targets)")
            target_columns = [row['name'] for row in cursor.fetchall()]
            print(f"Existing columns: {target_columns}")
            
            required_columns = [
                ('target_name', 'TEXT'),
                ('target_description', 'TEXT'),
                ('scope_coverage', 'TEXT'),
                ('baseline_year', 'TEXT'),
                ('baseline_co2e', 'REAL'),
                ('target_year', 'TEXT'),
                ('target_co2e', 'REAL'),
                ('target_reduction_pct', 'REAL'),
                ('target_type', 'TEXT'),
                ('sbti_approved', 'BOOLEAN'),
                ('status', 'TEXT'),
                ('progress_pct', 'REAL')
            ]
            
            for col_name, col_type in required_columns:
                if col_name not in target_columns:
                    print(f"Adding '{col_name}' column...")
                    try:
                        cursor.execute(f"ALTER TABLE carbon_targets ADD COLUMN {col_name} {col_type}")
                        print(f"Added '{col_name}'.")
                    except Exception as e:
                        print(f"Error adding '{col_name}': {e}")
                        
    except Exception as e:
        print(f"Error checking carbon_targets: {e}")

    # 3. Check sasb_standards
    print("\nChecking sasb_standards...")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sasb_standards'")
        if not cursor.fetchone():
            print("Creating sasb_standards table...")
            cursor.execute("""
                CREATE TABLE sasb_standards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    industry TEXT,
                    topic TEXT,
                    code TEXT,
                    metric TEXT,
                    unit TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created sasb_standards.")
    except Exception as e:
        print(f"Error checking sasb_standards: {e}")

    # 4. Check tcfd_recommendations
    print("\nChecking tcfd_recommendations...")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tcfd_recommendations'")
        if not cursor.fetchone():
            print("Creating tcfd_recommendations table...")
            cursor.execute("""
                CREATE TABLE tcfd_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    recommendation TEXT,
                    description TEXT,
                    guidance TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created tcfd_recommendations.")
    except Exception as e:
        print(f"Error checking tcfd_recommendations: {e}")

    # 5. Check tnfd_recommendations
    print("\nChecking tnfd_recommendations...")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tnfd_recommendations'")
        if not cursor.fetchone():
            print("Creating tnfd_recommendations table...")
            cursor.execute("""
                CREATE TABLE tnfd_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    recommendation TEXT,
                    description TEXT,
                    guidance TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created tnfd_recommendations.")
    except Exception as e:
        print(f"Error checking tnfd_recommendations: {e}")

    conn.commit()
    conn.close()
    print("\nSchema fix complete.")

if __name__ == "__main__":
    fix_schema()
