
import sqlite3
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.database import DB_PATH

# FORCE DB_PATH for remote environment to ensure correct DB is used
if os.path.exists('/var/www/sustainage/backend/data/sdg_desktop.sqlite'):
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def migrate():
    print(f"Migrating Supply Chain tables to {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Supplier Profiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS supplier_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        sector TEXT,
        region TEXT,
        contact_info TEXT,
        risk_score REAL DEFAULT 0, -- 0-100 scale
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Supplier Assessments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS supplier_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        assessment_date DATE,
        score REAL DEFAULT 0, -- 0-100 scale
        risk_level TEXT, -- 'Low', 'Medium', 'High'
        details TEXT, -- JSON storage for answers
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (supplier_id) REFERENCES supplier_profiles(id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("Supply Chain migration completed successfully.")

if __name__ == "__main__":
    migrate()
