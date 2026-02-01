import sqlite3
import os

DB_PATH = 'sustainage.db'

def init_economic_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Initializing Economic Module Tables...")
    
    # 1. investment_projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investment_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        project_name TEXT NOT NULL,
        description TEXT,
        initial_investment REAL DEFAULT 0,
        discount_rate REAL DEFAULT 0.10,
        start_date TEXT,
        duration_years INTEGER DEFAULT 5,
        status TEXT DEFAULT 'Planned',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("- investment_projects table created/verified.")

    # 2. investment_cash_flows
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investment_cash_flows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        year INTEGER NOT NULL,
        cash_flow REAL DEFAULT 0,
        description TEXT,
        FOREIGN KEY (project_id) REFERENCES investment_projects(id) ON DELETE CASCADE
    )
    """)
    print("- investment_cash_flows table created/verified.")

    # 3. investment_evaluations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investment_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        npv REAL,
        roi REAL,
        payback_period REAL,
        irr REAL,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES investment_projects(id) ON DELETE CASCADE
    )
    """)
    print("- investment_evaluations table created/verified.")
    
    conn.commit()
    conn.close()
    print("Economic Module Database Initialization Complete.")

if __name__ == "__main__":
    init_economic_tables()
