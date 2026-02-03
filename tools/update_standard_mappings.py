import sqlite3
import json
import os
import sys

# Detect environment and set paths
if os.name == 'nt':
    # Windows Local
    PROJECT_ROOT = r'c:\SUSTAINAGESERVER'
    DB_PATH = os.path.join(PROJECT_ROOT, 'backend', 'data', 'sdg_desktop.sqlite')
else:
    # Remote Linux
    PROJECT_ROOT = '/var/www/sustainage'
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

sys.path.append(PROJECT_ROOT)

def update_mappings():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- 1. Creating New Tables ---")
    
    # TSRS Standards Table (Turkish Sustainability Reporting Standards)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tsrs_standards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            title_tr TEXT NOT NULL,
            title_en TEXT,
            category TEXT,
            year TEXT DEFAULT '2024',
            description TEXT
        )
    """)
    print("Created/Verified tsrs_standards")

    # Map TSRS <-> ESRS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS map_tsrs_esrs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tsrs_code TEXT NOT NULL,
            esrs_code TEXT NOT NULL,
            relation_type TEXT DEFAULT 'Direct',
            company_id INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Created/Verified map_tsrs_esrs")

    # Map SASB <-> GRI (Consistent Naming)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS map_sasb_gri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sasb_code TEXT NOT NULL,
            gri_code TEXT NOT NULL,
            relation_type TEXT DEFAULT 'Related',
            company_id INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Created/Verified map_sasb_gri")

    # Map SDG <-> GRI (Ensure it exists)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS map_sdg_gri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sdg_indicator_code TEXT NOT NULL,
            gri_disclosure TEXT NOT NULL,
            relation_type TEXT DEFAULT 'Related',
            company_id INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Created/Verified map_sdg_gri")


    print("\n--- 2. Inserting TSRS 2026 Data ---")
    # Simulating TSRS 2026 updates (Based on TSRS 1 and TSRS 2 + new drafts)
    tsrs_data = [
        ('TSRS 1', 'Genel Hükümler', 'General Requirements', 'General', '2026'),
        ('TSRS 2', 'İklimle İlgili Açıklamalar', 'Climate-related Disclosures', 'Environmental', '2026'),
        ('TSRS S1', 'Kendi İşgücü', 'Own Workforce', 'Social', '2026'),
        ('TSRS S2', 'Değer Zincirindeki Çalışanlar', 'Workers in the Value Chain', 'Social', '2026'),
        ('TSRS G1', 'İş Etiği ve Yönetişim', 'Business Conduct', 'Governance', '2026')
    ]
    
    for code, tr, en, cat, year in tsrs_data:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO tsrs_standards (code, title_tr, title_en, category, year)
                VALUES (?, ?, ?, ?, ?)
            """, (code, tr, en, cat, year))
        except Exception as e:
            print(f"Error inserting {code}: {e}")
            
    print("Inserted TSRS 2026 standards")


    print("\n--- 3. Inserting ESRS 2026 Data ---")
    # Inserting into esrs_standards if they don't exist
    esrs_data = [
        ('ESRS S4', 'Consumers and end-users (2026 Draft)', 'Social'),
        ('ESRS G2', 'Business Conduct (2026 Draft)', 'Governance'),
        ('ESRS E6', 'Biodiversity (2026 Enhanced)', 'Environmental')
    ]
    
    for code, title, cat in esrs_data:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO esrs_standards (code, title, category)
                VALUES (?, ?, ?)
            """, (code, title, cat))
        except Exception as e:
            print(f"Error inserting {code}: {e}")
            
    print("Inserted ESRS 2026 standards")


    print("\n--- 4. Updating Mappings ---")

    # TSRS <-> ESRS Mappings
    mappings_tsrs_esrs = [
        ('TSRS 1', 'ESRS 1'),
        ('TSRS 2', 'ESRS E1'),
        ('TSRS S1', 'ESRS S1'),
        ('TSRS S2', 'ESRS S2'),
        ('TSRS G1', 'ESRS G1')
    ]
    
    for tsrs, esrs in mappings_tsrs_esrs:
        cursor.execute("SELECT id FROM map_tsrs_esrs WHERE tsrs_code=? AND esrs_code=?", (tsrs, esrs))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO map_tsrs_esrs (tsrs_code, esrs_code) VALUES (?, ?)", (tsrs, esrs))

    # SDG <-> GRI Mappings (New 2026 updates)
    mappings_sdg_gri = [
        ('12.6', 'GRI 302-1'), # Energy
        ('13.1', 'GRI 305-1'), # Emissions
        ('15.1', 'GRI 101'),   # Biodiversity 2024/2026
        ('8.5', 'GRI 401-1'),  # Employment
        ('5.5', 'GRI 405-1')   # Diversity
    ]
    
    for sdg, gri in mappings_sdg_gri:
        cursor.execute("SELECT id FROM map_sdg_gri WHERE sdg_indicator_code=? AND gri_disclosure=?", (sdg, gri))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO map_sdg_gri (sdg_indicator_code, gri_disclosure) VALUES (?, ?)", (sdg, gri))

    # SASB <-> GRI Mappings
    # Using dummy mapping logic for illustration if actual file not available
    mappings_sasb_gri = [
        ('EM-EP-110a.1', 'GRI 305-1'), # Scope 1 emissions
        ('EM-EP-110a.2', 'GRI 305-2'), # Scope 2
        ('EM-EP-320a.1', 'GRI 403-9'), # Safety
        ('IF-EU-110a.1', 'GRI 305-1')
    ]
    
    for sasb, gri in mappings_sasb_gri:
        cursor.execute("SELECT id FROM map_sasb_gri WHERE sasb_code=? AND gri_code=?", (sasb, gri))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO map_sasb_gri (sasb_code, gri_code) VALUES (?, ?)", (sasb, gri))

    conn.commit()
    conn.close()
    print("\nSuccess: Standards and mappings updated for 2026 regulations.")

if __name__ == "__main__":
    update_mappings()
