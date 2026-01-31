import sqlite3
import random
from datetime import datetime, timedelta
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def populate():
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    company_id = 1
    
    # Ensure company exists
    print("Checking Company...")
    cursor.execute("SELECT id FROM companies WHERE id=?", (company_id,))
    if not cursor.fetchone():
        print("Creating Test Company...")
        cursor.execute("INSERT INTO companies (id, name, sector, country, is_active) VALUES (?, ?, ?, ?, 1)", (company_id, 'Test Company', 'Technology', 'Turkey'))
    else:
        print("Test Company exists.")

    # 1. Carbon
    print("Populating Carbon...")
    scopes = ['Scope 1', 'Scope 2', 'Scope 3']
    cats = ['Stationary Combustion', 'Purchased Electricity', 'Business Travel']
    
    try:
        cursor.execute("SELECT count(*) FROM carbon_emissions")
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            period = date.strftime('%Y-%m')
            for scope, cat in zip(scopes, cats):
                # Removed description
                cursor.execute("""
                    INSERT INTO carbon_emissions (company_id, scope, category, source, quantity, unit, co2e_emissions, period, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (company_id, scope, cat, 'Diesel/Grid/Flight', random.uniform(100, 1000), 'liters/kWh/km', random.uniform(10, 500), period))
        print("Carbon populated.")
    except Exception as e:
        print(f"Carbon error: {e}")

    # 2. Energy
    print("Populating Energy...")
    try:
        cursor.execute("SELECT count(*) FROM energy_consumption")
        types = ['Electricity', 'Natural Gas']
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            year = date.year
            month = date.month
            for et in types:
                cursor.execute("""
                    INSERT INTO energy_consumption (company_id, energy_type, consumption_amount, unit, cost, year, month, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (company_id, et, random.uniform(500, 5000), 'kWh/m3', random.uniform(100, 1000), year, month))
        print("Energy populated.")
    except Exception as e:
        print(f"Energy error: {e}")

    # 3. Water
    print("Populating Water...")
    try:
        cursor.execute("SELECT count(*) FROM water_consumption")
        sources = ['Mains', 'Well']
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            year = date.year
            month = date.month
            for ws in sources:
                # Use consumption_type instead of water_source for main type
                cursor.execute("""
                    INSERT INTO water_consumption (company_id, consumption_type, consumption_amount, unit, cost, year, month, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (company_id, ws, random.uniform(50, 500), 'm3', random.uniform(20, 200), year, month))
        print("Water populated.")
    except Exception as e:
        print(f"Water error: {e}")

    # 4. Waste (waste_records)
    print("Populating Waste...")
    try:
        cursor.execute("SELECT count(*) FROM waste_records")
        # Need waste_type_id if possible, or just insert 0/1 if no FK constraint or if types exist
        # Check if waste_types table exists
        wtypes = []
        try:
            cursor.execute("SELECT id FROM waste_types")
            wtypes = [r[0] for r in cursor.fetchall()]
        except:
            pass
            
        if not wtypes:
             wtypes = [1, 2] # Dummy
             
        for i in range(12):
            date = datetime.now() - timedelta(days=30*i)
            period = date.strftime('%Y-%m')
            
            cursor.execute("""
                INSERT INTO waste_records (company_id, period, waste_type_id, waste_code, waste_name, quantity, unit, disposal_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, period, random.choice(wtypes), '08 01 11', 'Waste Paint', random.uniform(10, 100), 'kg', 'Recycling'))
        print("Waste populated.")
    except Exception as e:
        print(f"Waste error: {e}")

    # 5. GRI Responses (Company Info/GRI)
    print("Populating GRI Responses...")
    try:
        cursor.execute("SELECT count(*) FROM gri_responses")
        # GRI 2-1, 2-2 etc.
        indicators = [1, 2, 3, 4, 5] # Assuming IDs exist
        
        for i in range(1): # Just one set
            period = datetime.now().strftime('%Y')
            for ind in indicators:
                cursor.execute("""
                    INSERT INTO gri_responses (company_id, indicator_id, period, response_value, reporting_status)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, ind, period, "Sample GRI Response Text generated by AI...", "Final"))
        print("GRI populated.")
    except Exception as e:
        print(f"GRI error: {e}")

    # 6. GRI Company Details
    print("Populating GRI Company Details...")
    try:
        cursor.execute("SELECT count(*) FROM company_details_gri")
        # Check if exists
        cursor.execute("SELECT id FROM company_details_gri WHERE company_id=?", (company_id,))
        if cursor.fetchone():
             cursor.execute("""
                UPDATE company_details_gri 
                SET legal_name=?, description=?, mission=?
                WHERE company_id=?
             """, ('Test Company Legal Name', 'A leading tech company.', 'To sustain the future.', company_id))
        else:
             cursor.execute("""
                INSERT INTO company_details_gri (company_id, legal_name, description, mission, vision, tax_id, sector_details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
             """, (company_id, 'Test Company Legal Name', 'A leading tech company.', 'To sustain the future.', 'To be #1.', '1234567890', 'Software Development'))
        print("GRI Company Details populated.")
    except Exception as e:
        print(f"GRI Company Details error: {e}")

    conn.commit()
    conn.close()
    print("Done.")

if __name__ == '__main__':
    populate()
