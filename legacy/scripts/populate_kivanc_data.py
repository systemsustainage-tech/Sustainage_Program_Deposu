import sqlite3
import os
import random
from datetime import datetime

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

# Fallback for local testing
if not os.path.exists(DB_PATH):
    DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

def get_db():
    return sqlite3.connect(DB_PATH)

def populate():
    print(f"Connecting to {DB_PATH}...")
    conn = get_db()
    cursor = conn.cursor()

    # Drop tables to ensure clean slate with correct schema
    tables = ['carbon_emissions', 'energy_consumption', 'water_consumption', 'waste_generation', 'sdg_progress', 
              'governance_structure', 'social_employees', 'social_incidents', 'tnfd_recommendations', 'tcfd_risks', 
              'cbam_declarations', 'taxonomy_alignment']
    for t in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {t}")

    # Create Tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS carbon_emissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, scope TEXT, category TEXT, quantity REAL, unit TEXT, co2e_emissions REAL, period TEXT, created_at DATETIME
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS energy_consumption (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, energy_type TEXT, consumption_amount REAL, unit TEXT, cost REAL, year INTEGER, month INTEGER, created_at DATETIME
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS water_consumption (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, source_type TEXT, consumption_amount REAL, unit TEXT, year INTEGER, month INTEGER, created_at DATETIME
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS waste_generation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, waste_type TEXT, amount REAL, unit TEXT, disposal_method TEXT, date TEXT, created_at DATETIME
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sdg_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, goal_id INTEGER, progress REAL, year INTEGER
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS governance_structure (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, member_name TEXT, role TEXT, independent INTEGER
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS social_employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, count INTEGER, category TEXT, year INTEGER
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS social_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, incident_type TEXT, severity TEXT, date TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tnfd_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recommendation TEXT, status TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tcfd_risks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        risk_description TEXT, impact TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cbam_declarations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, declaration_date TEXT, amount REAL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS taxonomy_alignment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER, activity TEXT, alignment_percentage REAL
    )''')

    # 1. Company
    print("Creating Company...")
    cursor.execute("SELECT id FROM companies WHERE name LIKE 'Kıvanç Demir%'")
    row = cursor.fetchone()
    if row:
        company_id = row[0]
        print(f"Company exists with ID: {company_id}")
    else:
        cursor.execute("""
            INSERT INTO companies (name, sector, country, tax_number, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('Kıvanç Demir-Çelik', 'Iron & Steel', 'Turkey', '1234567890', 1, datetime.now()))
        company_id = cursor.lastrowid
        print(f"Created Company with ID: {company_id}")

    # 2. Clear old 2025 data to avoid duplicates (optional, but safer for re-runs)
    # We will just append for now or check before insert.

    # 3. Environmental Data (Carbon, Energy, Water, Waste)
    print("Inserting Environmental Data...")
    
    # Carbon
    scopes = ['Scope 1', 'Scope 2', 'Scope 3']
    for s in scopes:
        cursor.execute("""
            INSERT INTO carbon_emissions (company_id, scope, category, quantity, unit, co2e_emissions, period, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, s, 'General', random.uniform(1000, 5000), 'tCO2e', random.uniform(1000, 5000), '2025', datetime.now()))

    # Energy
    cursor.execute("""
        INSERT INTO energy_consumption (company_id, energy_type, consumption_amount, unit, cost, year, month, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (company_id, 'Electricity', 500000, 'kWh', 1500000, 2025, 1, datetime.now()))
    
    cursor.execute("""
        INSERT INTO energy_consumption (company_id, energy_type, consumption_amount, unit, cost, year, month, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (company_id, 'Natural Gas', 200000, 'm3', 800000, 2025, 1, datetime.now()))

    # Water
    cursor.execute("""
        INSERT INTO water_consumption (company_id, source_type, consumption_amount, unit, year, month, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (company_id, 'Mains Water', 15000, 'm3', 2025, 1, datetime.now()))
    
    cursor.execute("""
        INSERT INTO water_consumption (company_id, source_type, consumption_amount, unit, year, month, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (company_id, 'Recycled Water', 5000, 'm3', 2025, 1, datetime.now()))

    # Waste
    waste_types = ['Metal Scrap', 'Slag', 'General Waste', 'Hazardous Waste']
    for w in waste_types:
        cursor.execute("""
            INSERT INTO waste_generation (company_id, waste_type, amount, unit, disposal_method, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, w, random.uniform(100, 1000), 'tons', 'Recycling' if 'Hazardous' not in w else 'Special Treatment', '2025-01-01', datetime.now()))

    # 4. SDG Progress
    print("Inserting SDG Data...")
    for i in range(1, 18):
        # Check if table has year column, schema said yes
        try:
            cursor.execute("INSERT INTO sdg_progress (company_id, goal_id, progress, year) VALUES (?, ?, ?, ?)", 
                           (company_id, i, random.uniform(40, 95), 2025))
        except:
            # Maybe schema is different, try without company_id if fails (unlikely based on inspect)
            pass

    # 5. Governance
    print("Inserting Governance Data...")
    roles = ['CEO', 'CFO', 'CSO', 'Board Member', 'Independent Member']
    for r in roles:
        try:
            cursor.execute("INSERT INTO governance_structure (company_id, member_name, role, independent) VALUES (?, ?, ?, ?)",
                           (company_id, f"Name Surname {r}", r, 1 if 'Independent' in r else 0))
        except: pass

    # 6. TCFD & TNFD
    print("Inserting TCFD/TNFD Data...")
    try:
        cursor.execute("""
            INSERT INTO tnfd_recommendations (company_id, pillar, recommendation, status, details, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (company_id, 'Governance', 'Describe the board’s oversight of nature-related dependencies', 'Completed', 'Board reviews nature risks quarterly.', datetime.now()))
    except: pass
    
    # 7. Other Modules (Mocking existence if tables missing)
    # CSRD
    try:
        cursor.execute("INSERT INTO csrd_materiality (company_id, topic, impact_score, financial_score) VALUES (?, ?, ?, ?)",
                       (company_id, 'Climate Change', 4.5, 4.8))
    except: pass

    # Taxonomy
    try:
        cursor.execute("INSERT INTO taxonomy_alignment (company_id, activity_name, alignment_percentage) VALUES (?, ?, ?)",
                       (company_id, 'Manufacture of iron and steel', 85.5))
    except: pass
    
    # Biodiversity
    try:
        cursor.execute("INSERT INTO biodiversity_sites (company_id, site_name, proximity_to_protected_area) VALUES (?, ?, ?)",
                       (company_id, 'Main Plant - Gebze', 0))
    except: pass

    # 8. Register Report
    print("Registering Report...")
    try:
        # Check if report exists
        cursor.execute("SELECT id FROM report_registry WHERE company_id=? AND report_name LIKE 'Kivanc%'", (company_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO report_registry (
                    company_id, module_code, report_name, report_type, 
                    file_path, file_size, reporting_period, description, 
                    created_by, generated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, 'ALL', 'Kivanc Demir Celik Surdurulebilirlik Raporu 2025', 'DOCX',
                '/static/Kivanc_Demir_Celik_Surdurulebilirlik_Raporu_2025.docx', 102400, '2025',
                'Comprehensive Sustainability Report 2025', 1, datetime.now()
            ))
            print("Report registered.")
        else:
            print("Report already registered.")
    except Exception as e:
        print(f"Error registering report: {e}")

    conn.commit()
    conn.close()
    print("Data population complete.")

if __name__ == "__main__":
    populate()
