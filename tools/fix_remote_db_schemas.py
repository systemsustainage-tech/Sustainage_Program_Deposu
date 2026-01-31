
import sqlite3
import os

DB_PATH = '/var/www/sustainage/sustainage.db'

def fix_schemas():
    print(f"Connecting to {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("Database file not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. SDG Progress (for legacy fallback in sdg_add)
    print("Fixing sdg_progress...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sdg_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            goal_id INTEGER,
            target TEXT,
            action TEXT,
            status TEXT,
            progress_pct REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. TCFD Disclosures (Data entry table)
    # The existing table might be a master list. We need to check columns.
    # web_app.py inserts: company_id, year, category, disclosure, impact
    print("Fixing tcfd_disclosures...")
    try:
        cur.execute("ALTER TABLE tcfd_disclosures ADD COLUMN company_id INTEGER")
    except: pass
    try:
        cur.execute("ALTER TABLE tcfd_disclosures ADD COLUMN year INTEGER")
    except: pass
    try:
        cur.execute("ALTER TABLE tcfd_disclosures ADD COLUMN category TEXT")
    except: pass
    try:
        cur.execute("ALTER TABLE tcfd_disclosures ADD COLUMN disclosure TEXT")
    except: pass
    try:
        cur.execute("ALTER TABLE tcfd_disclosures ADD COLUMN impact TEXT")
    except: pass
    # If table didn't exist, create it
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tcfd_disclosures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            category TEXT,
            disclosure TEXT,
            impact TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. TNFD Disclosures
    # web_app.py inserts: company_id, year, pillar, disclosure, nature_impact
    print("Fixing tnfd_disclosures...")
    try:
        cur.execute("ALTER TABLE tnfd_disclosures ADD COLUMN company_id INTEGER")
    except: pass
    try:
        cur.execute("ALTER TABLE tnfd_disclosures ADD COLUMN year INTEGER")
    except: pass
    try:
        cur.execute("ALTER TABLE tnfd_disclosures ADD COLUMN pillar TEXT")
    except: pass
    try:
        cur.execute("ALTER TABLE tnfd_disclosures ADD COLUMN disclosure TEXT")
    except: pass
    try:
        cur.execute("ALTER TABLE tnfd_disclosures ADD COLUMN nature_impact TEXT")
    except: pass
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tnfd_disclosures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            pillar TEXT,
            disclosure TEXT,
            nature_impact TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. SASB Responses
    print("Fixing sasb tables...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sasb_disclosures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            topic TEXT,
            metric TEXT,
            value TEXT,
            unit TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Add columns if missing
    for col in ['company_id', 'year', 'topic', 'metric', 'value', 'unit']:
        try:
            cur.execute(f"ALTER TABLE sasb_disclosures ADD COLUMN {col} TEXT")
        except: pass

    # 5. GRI Responses (gri_add uses gri_data)
    # web_app.py inserts: company_id, year, standard, disclosure, value
    print("Fixing gri_data...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gri_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            year INTEGER,
            standard TEXT,
            disclosure TEXT,
            value TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    for col in ['company_id', 'year', 'standard', 'disclosure', 'value']:
        try:
            cur.execute(f"ALTER TABLE gri_data ADD COLUMN {col} TEXT")
        except: pass

    conn.commit()
    conn.close()
    print("Schema fix complete.")

if __name__ == "__main__":
    fix_schemas()
