import sqlite3
import os
import sys

# Adjust path to find config
sys.path.append('/var/www/sustainage')

try:
    from config.database import DB_PATH
except ImportError:
    # Fallback if config module not found or path wrong
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    print(f"Checking database at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create missing tables
    tables = {
        "sasb_standards": """
            CREATE TABLE IF NOT EXISTS sasb_standards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                sector TEXT,
                topic TEXT,
                metric TEXT,
                unit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "tcfd_recommendations": """
            CREATE TABLE IF NOT EXISTS tcfd_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pillar TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "tnfd_recommendations": """
            CREATE TABLE IF NOT EXISTS tnfd_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pillar TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "carbon_targets": """
            CREATE TABLE IF NOT EXISTS carbon_targets (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                target_name TEXT NOT NULL,
                target_description TEXT,
                scope_coverage TEXT NOT NULL,
                baseline_year INTEGER NOT NULL,
                baseline_co2e REAL NOT NULL,
                target_year INTEGER NOT NULL,
                target_co2e REAL NOT NULL,
                target_reduction_pct REAL,
                target_type TEXT,
                intensity_metric TEXT,
                commitment_level TEXT,
                sbti_approved BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'active',
                progress_pct REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """,
        "carbon_reduction_initiatives": """
            CREATE TABLE IF NOT EXISTS carbon_reduction_initiatives (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                initiative_name TEXT NOT NULL,
                initiative_description TEXT,
                initiative_type TEXT,
                target_scope TEXT,
                start_date DATE,
                end_date DATE,
                investment_amount REAL,
                expected_reduction_co2e REAL,
                actual_reduction_co2e REAL,
                status TEXT DEFAULT 'planned',
                roi_years REAL,
                sdg_alignment TEXT,
                responsible_person TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """,
        "carbon_reports": """
            CREATE TABLE IF NOT EXISTS carbon_reports (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                report_period TEXT NOT NULL,
                report_type TEXT,
                scope1_total REAL,
                scope2_total REAL,
                scope3_total REAL,
                total_co2e REAL NOT NULL,
                boundary_description TEXT,
                base_year INTEGER,
                reporting_standard TEXT DEFAULT 'GHG Protocol',
                verification_status TEXT,
                verifier_name TEXT,
                verification_date DATE,
                report_file_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """
    }

    for table_name, create_sql in tables.items():
        try:
            print(f"Checking/Creating table: {table_name}")
            cursor.execute(create_sql)
            conn.commit()
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")

    # 2. Add missing columns to carbon_emissions
    columns_to_check = {
        "carbon_emissions": [
            ("data_json", "TEXT"),
            ("fuel_type", "TEXT"),
            ("subcategory", "TEXT"),
            ("evidence_file", "TEXT"),
            ("emission_factor_source", "TEXT"),
            ("calculation_method", "TEXT"),
            ("data_quality", "TEXT DEFAULT 'measured'"),
            ("verified", "BOOLEAN DEFAULT 0"),
            ("verified_by", "TEXT"),
            ("verified_at", "TEXT")
        ],
        "audit_logs": [
            ("payload_json", "TEXT")
        ]
    }

    for table, cols in columns_to_check.items():
        print(f"Checking columns for table: {table}")
        try:
            # Check if table exists first
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                print(f"Table {table} does not exist, skipping column checks.")
                continue

            # Get existing columns
            cursor.execute(f"PRAGMA table_info({table})")
            existing_cols = {row[1] for row in cursor.fetchall()}
            
            for col_name, col_def in cols:
                if col_name not in existing_cols:
                    print(f"Adding column {col_name} to {table}...")
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                        conn.commit()
                        print(f"Added {col_name}.")
                    except Exception as e:
                        print(f"Error adding column {col_name}: {e}")
                else:
                    print(f"Column {col_name} already exists.")
                    
        except Exception as e:
            print(f"Error processing table {table}: {e}")

    conn.close()
    print("Schema fix completed.")

if __name__ == "__main__":
    fix_schema()
