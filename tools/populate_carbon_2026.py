import sqlite3
import ftplib
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Load environment variables
load_dotenv()

FTP_HOST = os.getenv('FTP_HOST', '72.62.150.207')
FTP_USER = os.getenv('FTP_USER', 'cursorsustainageftp')
FTP_PASS = os.getenv('FTP_PASS', 'Kayra_1507_Sk!')

LOCAL_DB_PATH = 'temp_carbon_pop.sqlite'

def main():
    try:
        print(f"Connecting to FTP {FTP_HOST}...")
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")

        remote_path = '/httpdocs/backend/data/sdg_desktop.sqlite'
        
        print(f"Downloading {remote_path}...")
        with open(LOCAL_DB_PATH, 'wb') as f:
            ftp.retrbinary(f"RETR {remote_path}", f.write)
        print("Download complete.")
        
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()

        company_id = 1
        year = 2026

        # Populate scope1_emissions
        print("Populating scope1_emissions...")
        cursor.execute("DROP TABLE IF EXISTS scope1_emissions") # Re-create to ensure clean state or schema match
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scope1_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                emission_source TEXT NOT NULL,
                fuel_type TEXT,
                fuel_consumption REAL,
                fuel_unit TEXT,
                emission_factor REAL,
                total_emissions REAL,
                invoice_date TEXT,
                due_date TEXT,
                supplier TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        cursor.execute("""
            INSERT INTO scope1_emissions (company_id, year, emission_source, fuel_type, fuel_consumption, fuel_unit, emission_factor, total_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, year, 'Heating', 'Natural Gas', 1000, 'm3', 2.16, 2160))
        cursor.execute("""
            INSERT INTO scope1_emissions (company_id, year, emission_source, fuel_type, fuel_consumption, fuel_unit, emission_factor, total_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, year, 'Fleet', 'Diesel', 500, 'L', 2.68, 1340))

        # Populate scope2_emissions
        print("Populating scope2_emissions...")
        cursor.execute("DROP TABLE IF EXISTS scope2_emissions")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scope2_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                energy_source TEXT NOT NULL,
                energy_consumption REAL,
                energy_unit TEXT,
                grid_emission_factor REAL,
                total_emissions REAL,
                invoice_date TEXT,
                due_date TEXT,
                supplier TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        cursor.execute("""
            INSERT INTO scope2_emissions (company_id, year, energy_source, energy_consumption, energy_unit, grid_emission_factor, total_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, year, 'Grid Electricity', 5000, 'kWh', 0.526, 2630))

        # Populate scope3_emissions
        print("Populating scope3_emissions...")
        cursor.execute("DROP TABLE IF EXISTS scope3_emissions")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scope3_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                activity_data REAL,
                activity_unit TEXT,
                emission_factor REAL,
                total_emissions REAL,
                invoice_date TEXT,
                due_date TEXT,
                supplier TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        cursor.execute("""
            INSERT INTO scope3_emissions (company_id, year, category, subcategory, activity_data, activity_unit, emission_factor, total_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, year, 'Business Travel', 'Air Travel', 2000, 'km', 0.255, 510))

        # Populate carbon_emissions (for Dashboard)
        print("Populating carbon_emissions...")
        cursor.execute("DROP TABLE IF EXISTS carbon_emissions")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carbon_emissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                period TEXT,
                scope TEXT,
                category TEXT,
                quantity REAL,
                unit TEXT,
                co2e_emissions REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Insert summary records
        cursor.execute("""
            INSERT INTO carbon_emissions (company_id, period, scope, category, quantity, unit, co2e_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, '2026', 'Scope 1', 'Heating', 1000, 'm3', 2160))
        cursor.execute("""
            INSERT INTO carbon_emissions (company_id, period, scope, category, quantity, unit, co2e_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, '2026', 'Scope 2', 'Electricity', 5000, 'kWh', 2630))
        cursor.execute("""
            INSERT INTO carbon_emissions (company_id, period, scope, category, quantity, unit, co2e_emissions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, '2026', 'Scope 3', 'Travel', 2000, 'km', 510))
        
        # Populate emission_factors
        print("Populating emission_factors...")
        cursor.execute("DROP TABLE IF EXISTS emission_factors")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emission_factors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                fuel_type TEXT,
                factor_value REAL NOT NULL,
                unit TEXT NOT NULL,
                scope INTEGER,
                country TEXT,
                source_reference TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        factors = [
            ('Doğal Gaz', 'Natural Gas', 2.16, 'kg CO2/m3', 1, 'Turkey', 'TUIK'),
            ('Motorin', 'Diesel', 2.68, 'kg CO2/L', 1, 'Turkey', 'TUIK'),
            ('Elektrik', 'Electricity', 0.526, 'kg CO2/kWh', 2, 'Turkey', 'TEIAS'),
            ('Havayolu', 'Air Travel', 0.255, 'kg CO2/km', 3, 'Global', 'ICAO')
        ]
        for f in factors:
             cursor.execute("""
                INSERT INTO emission_factors (source, fuel_type, factor_value, unit, scope, country, source_reference)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, f)

        conn.commit()
        conn.close()
        print("\nDatabase populated locally.")

        print(f"Uploading updated DB to {remote_path}...")
        with open(LOCAL_DB_PATH, 'rb') as f:
            ftp.storbinary(f"STOR {remote_path}", f)
        print("Upload complete.")
        
        ftp.quit()
        
        # Clean up
        if os.path.exists(LOCAL_DB_PATH):
            os.remove(LOCAL_DB_PATH)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
