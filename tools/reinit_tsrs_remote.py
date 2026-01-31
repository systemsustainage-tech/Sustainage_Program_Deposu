import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def reinit_tsrs():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Drop table if exists
    try:
        cur.execute("DROP TABLE IF EXISTS tsrs_assessment")
        print("Dropped tsrs_assessment table.")
    except Exception as e:
        print(f"Error dropping table: {e}")

    # Create table with correct schema
    create_sql = """
    CREATE TABLE tsrs_assessment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        reporting_period VARCHAR(20),
        section_id VARCHAR(50),
        question_id VARCHAR(50),
        answer TEXT,
        score REAL,
        evidence_file VARCHAR(255),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    try:
        cur.execute(create_sql)
        print("Created tsrs_assessment table with reporting_period column.")
    except Exception as e:
        print(f"Error creating table: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reinit_tsrs()
