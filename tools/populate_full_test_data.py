
import sqlite3
import os
import random
from datetime import datetime, timedelta

# DB Path on Server
DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def get_db():
    return sqlite3.connect(DB_PATH)

def populate():
    print(f"Connecting to {DB_PATH}...")
    try:
        conn = get_db()
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. Ensure Test Company Exists
    print("Checking Test Company...")
    cursor = conn.execute("SELECT id FROM companies WHERE id=1")
    if not cursor.fetchone():
        print("Creating Test Company...")
        conn.execute("""
            INSERT INTO companies (id, name, sector, country, tax_number, is_active)
            VALUES (1, 'Test Company A.Ş.', 'Manufacturing', 'Turkey', '1234567890', 1)
        """)
    else:
        print("Test Company exists.")

    company_id = 1
    
    # 2. Populate Carbon Data (Scope 1, 2, 3)
    print("Populating Carbon Data...")
    conn.execute("DELETE FROM carbon_emissions WHERE company_id=?", (company_id,))
    
    scopes = ['Scope 1', 'Scope 2', 'Scope 3']
    categories = {
        'Scope 1': ['Stationary Combustion', 'Mobile Combustion', 'Fugitive Emissions'],
        'Scope 2': ['Purchased Electricity', 'Steam'],
        'Scope 3': ['Purchased Goods', 'Capital Goods', 'Fuel-and-Energy Related Activities', 'Upstream Transportation', 'Waste Generated in Operations', 'Business Travel', 'Employee Commuting']
    }
    
    for scope in scopes:
        for cat in categories[scope]:
            # Generate 12 months of data for 2024
            for month in range(1, 13):
                period = f"2024-{month:02d}"
                qty = random.uniform(100, 5000)
                unit = 'liters' if scope == 'Scope 1' else 'kWh' if scope == 'Scope 2' else 'kg'
                co2 = qty * (0.5 if scope == 'Scope 2' else 2.5) # Fake factors
                
                conn.execute("""
                    INSERT INTO carbon_emissions (company_id, period, scope, category, quantity, unit, co2e_emissions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (company_id, period, scope, cat, qty, unit, co2))

    # 3. Populate Energy Data
    print("Populating Energy Data...")
    conn.execute("DELETE FROM energy_consumption WHERE company_id=?", (company_id,))
    energy_types = ['Electricity', 'Natural Gas', 'Diesel']
    
    for et in energy_types:
        for month in range(1, 13):
            cons = random.uniform(1000, 50000)
            unit = 'kWh' if et == 'Electricity' else 'm3' if et == 'Natural Gas' else 'liters'
            cost = cons * (2.5 if et == 'Electricity' else 10.0)
            
            conn.execute("""
                INSERT INTO energy_consumption (company_id, year, month, energy_type, consumption_amount, unit, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, '2024', f"{month:02d}", et, cons, unit, cost))

    # 4. Populate Water Data
    print("Populating Water Data...")
    conn.execute("DELETE FROM water_consumption WHERE company_id=?", (company_id,))
    water_sources = ['Mains', 'Groundwater', 'Rainwater']
    
    for ws in water_sources:
        for month in range(1, 13):
            amount = random.uniform(50, 1000)
            cost = amount * 15.0
            
            # Try to handle both water_source and consumption_type columns
            # Check schema first or just try inserting with both if possible, or update based on error
            # Error said: NOT NULL constraint failed: water_consumption.consumption_type
            # So we must provide consumption_type.
            
            conn.execute("""
                INSERT INTO water_consumption (company_id, year, month, water_source, consumption_type, consumption_amount, unit, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, '2024', f"{month:02d}", ws, ws, amount, 'm3', cost))

    # 5. Populate Waste Data
    print("Populating Waste Data...")
    conn.execute("DELETE FROM waste_generation WHERE company_id=?", (company_id,))
    
    # Check/Populate waste_types if needed
    waste_types_map = {}
    waste_types = ['Paper', 'Plastic', 'Metal', 'Hazardous']
    try:
        # Drop waste_types to ensure schema is correct (for test data population)
        conn.execute("DROP TABLE IF EXISTS waste_types")
        
        # Create waste_types
        conn.execute("""
            CREATE TABLE waste_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT
            )
        """)
        
        for wt in waste_types:
            # Check if exists
            cur = conn.execute("SELECT id FROM waste_types WHERE name=?", (wt,))
            row = cur.fetchone()
            if row:
                waste_types_map[wt] = row[0]
            else:
                cur = conn.execute("INSERT INTO waste_types (name, category) VALUES (?, ?)", (wt, 'General'))
                waste_types_map[wt] = cur.lastrowid
    except Exception as e:
        print(f"Error handling waste_types: {e}")
        # Fallback map
        for i, wt in enumerate(waste_types, 1):
            waste_types_map[wt] = i

    # Check if waste_records exists
    try:
        conn.execute("DELETE FROM waste_records WHERE company_id=?", (company_id,))
        use_waste_records = True
    except:
        use_waste_records = False
        
    methods = ['Recycling', 'Landfill', 'Incineration']
    
    for wt in waste_types:
        for month in range(1, 13):
            period = f"2024-{month:02d}"
            qty = random.uniform(10, 500)
            method = random.choice(methods)
            wt_id = waste_types_map.get(wt, 1)
            
            if use_waste_records:
                # Error said: NOT NULL constraint failed: waste_records.period
                # Error said: NOT NULL constraint failed: waste_records.waste_type_id
                # Error said: NOT NULL constraint failed: waste_records.waste_code
                conn.execute("""
                    INSERT INTO waste_records (company_id, waste_name, quantity, unit, disposal_method, created_at, period, waste_type_id, waste_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id, wt, qty, 'kg', method, f"{period}-01 00:00:00", period, wt_id, '20 01 01'))
                
                # Also insert into waste_generation to be safe for other parts of the app
                conn.execute("""
                    INSERT INTO waste_generation (company_id, period, waste_type, waste_amount, amount, unit, disposal_method, year, month, waste_category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id, period, wt, qty, qty, 'kg', method, '2024', f"{month:02d}", 'General'))
            else:
                 conn.execute("""
                    INSERT INTO waste_generation (company_id, period, waste_type, waste_amount, amount, unit, disposal_method, year, month, waste_category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id, period, wt, qty, qty, 'kg', method, '2024', f"{month:02d}", 'General'))

    # 6. Populate GRI Info
    print("Populating GRI Info...")
    conn.execute("DELETE FROM company_details_gri WHERE company_id=?", (company_id,))
    conn.execute("""
        INSERT INTO company_details_gri (
            company_id, legal_name, address, contact_person, phone, email, website,
            founded_year, employee_count, description, mission, vision, tax_id, sector_details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (company_id, 'Test Company A.Ş.', 'Organize Sanayi Bölgesi 1. Cadde No:5, Istanbul', 
          'Ahmet Yılmaz', '+90 212 555 1234', 'info@testcompany.com.tr', 'www.testcompany.com.tr',
          1995, 250, 
          'Leading manufacturer of automotive parts with a focus on sustainability.',
          'To be the most sustainable automotive supplier in the region.',
          'Zero emission production by 2030.',
          '1234567890', 'Automotive Parts Manufacturing'))

    conn.commit()
    conn.close()
    print("Population complete.")

if __name__ == '__main__':
    populate()
