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
    print(f"Migrating LCA tables to {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. LCA Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lca_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        unit TEXT, -- e.g. 'piece', 'kg'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. LCA Assessments Table (Versions of analysis)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lca_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        name TEXT NOT NULL, -- e.g. '2025 Base Scenario'
        assessment_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES lca_products(id)
    )
    """)
    
    # 3. LCA Entries Table (Data points)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lca_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL,
        company_id INTEGER NOT NULL,
        stage TEXT NOT NULL, -- 'raw_material', 'production', 'distribution', 'use', 'end_of_life'
        item_name TEXT NOT NULL, -- e.g. 'Steel', 'Electricity', 'Transport'
        quantity REAL DEFAULT 0,
        unit TEXT, -- e.g. 'kg', 'kWh', 'km'
        co2e_factor REAL DEFAULT 0, -- kg CO2e per unit
        energy_consumption REAL DEFAULT 0, -- MJ or kWh
        water_consumption REAL DEFAULT 0, -- Liters
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assessment_id) REFERENCES lca_assessments(id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("LCA migration completed successfully.")

if __name__ == "__main__":
    migrate()
