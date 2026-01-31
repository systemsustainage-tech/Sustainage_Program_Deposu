import sqlite3
import os
import sys

# Define database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'data', 'sdg_desktop.sqlite')

def init_schema():
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop existing tables to ensure clean schema
    tables = ['sdg_responses', 'sdg_indicators', 'sdg_targets', 'sdg_goals']
    for table in tables:
        print(f"Dropping table {table}...")
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    # 1. SDG Goals
    print("Creating table sdg_goals...")
    cursor.execute("""
        CREATE TABLE sdg_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL, -- e.g. "1", "2"
            name_tr TEXT NOT NULL,
            name_en TEXT,
            description_tr TEXT,
            description_en TEXT,
            parent_id INTEGER, -- Self-referencing if needed, usually NULL for top-level goals
            icon TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. SDG Targets
    print("Creating table sdg_targets...")
    cursor.execute("""
        CREATE TABLE sdg_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL, -- e.g. "1.1", "1.2"
            name_tr TEXT NOT NULL,
            name_en TEXT,
            description_tr TEXT,
            description_en TEXT,
            parent_id INTEGER NOT NULL, -- References sdg_goals.id
            goal_id INTEGER, -- Redundant but useful alias for parent_id if needed, we stick to parent_id as requested
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES sdg_goals(id) ON DELETE CASCADE
        )
    """)

    # 3. SDG Indicators
    print("Creating table sdg_indicators...")
    cursor.execute("""
        CREATE TABLE sdg_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL, -- e.g. "1.1.1"
            name_tr TEXT NOT NULL,
            name_en TEXT,
            description_tr TEXT,
            description_en TEXT,
            parent_id INTEGER NOT NULL, -- References sdg_targets.id
            target_id INTEGER, -- Alias for parent_id
            
            -- Integration mappings (JSON or specific fields)
            gri_mapping TEXT, -- GRI connection
            tsrs_mapping TEXT, -- TSRS connection
            esrs_mapping TEXT, -- ESRS connection
            
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES sdg_targets(id) ON DELETE CASCADE
        )
    """)

    # 4. SDG Responses (User Data)
    print("Creating table sdg_responses...")
    cursor.execute("""
        CREATE TABLE sdg_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL, -- Assuming multi-tenant or single company
            indicator_id INTEGER NOT NULL,
            period TEXT NOT NULL, -- e.g. "2023", "2023-Q1"
            
            value TEXT, -- The actual data value (numeric or text)
            unit TEXT, -- Unit of measurement
            evidence TEXT, -- Evidence description or file path/URL
            
            status TEXT DEFAULT 'pending', -- pending, approved, rejected
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (indicator_id) REFERENCES sdg_indicators(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("Schema initialization completed successfully.")

if __name__ == "__main__":
    init_schema()
