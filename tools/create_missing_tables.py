import sqlite3
import os

DB_PATH = "/var/www/sustainage/data/sdg_desktop.sqlite"

def create_tables():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Creating Missing Tables ---")

    # Governance Board Stats
    print("Creating governance_board_stats...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS governance_board_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            total_members INTEGER DEFAULT 0,
            female_members INTEGER DEFAULT 0,
            independent_members INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Governance Ethics
    print("Creating governance_ethics...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS governance_ethics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            training_hours REAL DEFAULT 0,
            reports_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Economic Climate Impact
    print("Creating economic_climate_impact...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economic_climate_impact (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            financial_impact REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    create_tables()
