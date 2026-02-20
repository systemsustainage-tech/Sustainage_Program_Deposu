import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def fix_schema():
    if not os.path.exists(DB_PATH):
        logging.error(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. report_registry
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS report_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                module_code TEXT,
                report_name TEXT,
                report_type TEXT,
                file_path TEXT,
                file_size INTEGER,
                reporting_period TEXT,
                description TEXT,
                created_by INTEGER,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logging.info("Created report_registry table.")
    except Exception as e:
        logging.error(f"Error creating report_registry: {e}")

    # 2. carbon_emissions
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS carbon_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT,
                category TEXT,
                quantity REAL,
                unit TEXT,
                co2e_emissions REAL,
                period TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logging.info("Created carbon_emissions table.")
    except Exception as e:
        logging.error(f"Error creating carbon_emissions: {e}")

    # 3. tnfd_recommendations
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tnfd_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pillar TEXT,
                recommendation TEXT,
                guidance TEXT
            )
        """)
        logging.info("Created tnfd_recommendations table.")
        
        # Insert sample data if empty
        count = cur.execute("SELECT COUNT(*) FROM tnfd_recommendations").fetchone()[0]
        if count == 0:
            cur.execute("INSERT INTO tnfd_recommendations (pillar, recommendation, guidance) VALUES ('Governance', 'Describe the organization’s governance of nature-related dependencies, impacts, risks and opportunities.', 'Board oversight and management role')")
            logging.info("Inserted sample TNFD data.")
            
    except Exception as e:
        logging.error(f"Error creating tnfd_recommendations: {e}")

    conn.commit()
    conn.close()
    logging.info("Schema fix completed.")

if __name__ == "__main__":
    fix_schema()
