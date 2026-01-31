
import sqlite3
import datetime
import os

DB_PATHS = ['backend/data/sdg_desktop.sqlite', '/var/www/sustainage/sustainage.db', 'sustainage.db']
DB_PATH = None
for p in DB_PATHS:
    if os.path.exists(p):
        DB_PATH = p
        break

if not DB_PATH:
    print(f"Database not found. Checked: {DB_PATHS}")
    exit(1)

def update_gri_standards():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gri_standards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            title TEXT,
            category TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sector TEXT DEFAULT 'General'
        )
    """)
    
    # Check if sector column exists (for existing tables)
    cursor.execute("PRAGMA table_info(gri_standards)")
    cols = [c[1] for c in cursor.fetchall()]
    
    if 'sector' not in cols:
        print("Adding sector column...")
        cursor.execute("ALTER TABLE gri_standards ADD COLUMN sector TEXT DEFAULT 'General'")
    
    # Add new standards
    new_standards = [
        ('GRI 11', 'Oil and Gas Sector 2021', 'Sector', 'Oil and Gas Sector Standard'),
        ('GRI 12', 'Coal Sector 2022', 'Sector', 'Coal Sector Standard'),
        ('GRI 13', 'Agriculture, Aquaculture and Fishing Sectors 2022', 'Sector', 'Agriculture, Aquaculture and Fishing Sectors Standard'),
        ('GRI 14', 'Mining Sector 2024', 'Sector', 'Mining Sector Standard'),
        ('GRI 101', 'Biodiversity 2024', 'Topic', 'Biodiversity Standard (Updated)')
    ]
    
    for code, title, cat, desc in new_standards:
        # Check if exists
        cursor.execute("SELECT id FROM gri_standards WHERE code = ?", (code,))
        row = cursor.fetchone()
        if not row:
            print(f"Inserting {code}...")
            cursor.execute("""
                INSERT INTO gri_standards (code, title, category, description, created_at, sector)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (code, title, cat, desc, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                  cat if cat == 'Sector' else 'General'))
        else:
            print(f"Updating {code}...")
            cursor.execute("""
                UPDATE gri_standards SET title=?, category=?, description=?, sector=?
                WHERE code=?
            """, (title, cat, desc, cat if cat == 'Sector' else 'General', code))

    conn.commit()
    conn.close()
    print("GRI Standards updated.")

if __name__ == "__main__":
    update_gri_standards()
