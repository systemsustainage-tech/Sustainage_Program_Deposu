import sqlite3
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "sdg_desktop.sqlite")
JSON_PATH = os.path.join(BASE_DIR, "backend", "data", "sdg_data_dump.json")

# Local Schemas (Source of Truth)
SCHEMAS = {
    'sdg_goals': """
        CREATE TABLE sdg_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code INTEGER UNIQUE NOT NULL,
            title_tr TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    'sdg_targets': """
        CREATE TABLE sdg_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            title_tr TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_id) REFERENCES sdg_goals(id)
        )
    """,
    'sdg_indicators': """
        CREATE TABLE sdg_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            title_tr TEXT NOT NULL,
            data_source TEXT,
            measurement_frequency TEXT,
            related_sectors TEXT,
            related_funds TEXT,
            kpi_metric TEXT,
            implementation_requirement TEXT,
            notes TEXT,
            request_status TEXT,
            status TEXT,
            progress_percentage REAL,
            completeness_percentage REAL,
            policy_document_exists TEXT,
            data_quality TEXT,
            incentive_readiness_score REAL,
            readiness_level TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_id) REFERENCES sdg_targets(id)
        )
    """,
    'sdg_question_bank': """
        CREATE TABLE sdg_question_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_id INTEGER,
            question_text TEXT NOT NULL,
            question_type TEXT,
            options TEXT,
            required INTEGER DEFAULT 0,
            order_num INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (indicator_id) REFERENCES sdg_indicators(id)
        )
    """
}

def import_data():
    if not os.path.exists(JSON_PATH):
        print(f"JSON dump not found at {JSON_PATH}")
        return

    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tables in dependency order (reverse for drop, forward for create/insert)
        tables = ['sdg_goals', 'sdg_targets', 'sdg_indicators', 'sdg_question_bank']
        
        print("--- Recreating Tables ---")
        # Disable foreign keys temporarily to allow dropping tables in any order (though we try to be nice)
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        for table in reversed(tables):
            print(f"Dropping {table}...")
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
        for table in tables:
            print(f"Creating {table}...")
            cursor.execute(SCHEMAS[table])
            
        # Re-enable foreign keys (optional, but good practice if we want to check integrity later)
        # cursor.execute("PRAGMA foreign_keys = ON") # Keeping off during bulk insert is faster/safer against order issues
            
        print("\n--- Importing Data ---")
        for table in tables:
            if table not in data:
                print(f"Skipping {table} (not in dump)")
                continue
                
            records = data[table]
            if not records:
                print(f"Skipping {table} (no records)")
                continue
                
            print(f"Importing {len(records)} records into {table}...")
            
            # Get columns from the first record
            columns = list(records[0].keys())
            placeholders = ', '.join(['?' for _ in columns])
            col_names = ', '.join(columns)
            
            query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            
            inserted_count = 0
            for record in records:
                values = [record[col] for col in columns]
                try:
                    cursor.execute(query, values)
                    inserted_count += 1
                except Exception as e:
                    print(f"Error inserting into {table} (ID {record.get('id')}): {e}")
            
            print(f"  - {inserted_count} records inserted.")
            
        conn.commit()
        print("Data import and schema migration completed successfully.")
        conn.close()
        
    except Exception as e:
        print(f"Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import_data()
