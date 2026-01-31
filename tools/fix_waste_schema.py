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

LOCAL_DB_PATH = 'temp_waste_fix.sqlite'

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

        # Create waste_records table (Schema from waste_manager.py)
        print("Creating waste_records table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                waste_type_id INTEGER NOT NULL,
                waste_code TEXT NOT NULL,
                waste_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                source_location TEXT,
                generation_source TEXT,
                disposal_method TEXT,
                recycling_rate REAL DEFAULT 0.0,
                disposal_cost REAL DEFAULT 0.0,
                carbon_footprint REAL DEFAULT 0.0,
                invoice_date TEXT,
                due_date TEXT,
                supplier TEXT,
                data_quality TEXT DEFAULT 'Estimated',
                evidence_file TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        
        # Create waste_types if not exists (needed for FK, though SQLite FKs are loose by default unless enabled)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waste_code TEXT UNIQUE NOT NULL,
                waste_name TEXT NOT NULL,
                waste_category TEXT NOT NULL,
                hazard_level TEXT DEFAULT 'Non-hazardous',
                recycling_potential TEXT DEFAULT 'Medium',
                disposal_method TEXT,
                environmental_impact TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check if waste_types is empty, populate if needed
        cursor.execute("SELECT COUNT(*) FROM waste_types")
        if cursor.fetchone()[0] == 0:
            print("Populating waste_types...")
            waste_types = [
                ('15 01 01', 'Kağıt ve Karton Ambalaj', 'Ambalaj Atığı', 'Non-hazardous', 'High', 'Recycling', 'Low', 'Paper packaging'),
                ('15 01 02', 'Plastik Ambalaj', 'Ambalaj Atığı', 'Non-hazardous', 'High', 'Recycling', 'Medium', 'Plastic packaging'),
                ('20 01 01', 'Kağıt ve Karton', 'Belediye Atığı', 'Non-hazardous', 'High', 'Recycling', 'Low', 'Office paper'),
                ('20 03 01', 'Karışık Belediye Atığı', 'Belediye Atığı', 'Non-hazardous', 'Low', 'Landfill', 'Medium', 'General waste')
            ]
            cursor.executemany("""
                INSERT INTO waste_types (waste_code, waste_name, waste_category, hazard_level, recycling_potential, disposal_method, environmental_impact, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, waste_types)

        # Populate waste_records with sample data for 2026
        print("Populating waste_records for 2026...")
        # Get waste_type_ids
        cursor.execute("SELECT id, waste_code, waste_name FROM waste_types")
        types = cursor.fetchall()
        
        company_id = 1
        year = '2026'
        
        # Sample records
        records = [
            (company_id, year, types[0][0], types[0][1], types[0][2], 500, 'kg', 'Warehouse', 'Packaging', 'Recycling', 100, 0, 0, '2026-01-15', '2026-02-15', 'Recycle Co'),
            (company_id, year, types[1][0], types[1][1], types[1][2], 200, 'kg', 'Warehouse', 'Packaging', 'Recycling', 100, 0, 0, '2026-01-15', '2026-02-15', 'Recycle Co'),
            (company_id, year, types[3][0], types[3][1], types[3][2], 1000, 'kg', 'Office', 'General', 'Landfill', 0, 500, 100, '2026-01-20', '2026-02-20', 'Municipality')
        ]
        
        cursor.executemany("""
            INSERT INTO waste_records (
                company_id, period, waste_type_id, waste_code, waste_name, 
                quantity, unit, source_location, generation_source, disposal_method, 
                recycling_rate, disposal_cost, carbon_footprint, 
                invoice_date, due_date, supplier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)

        conn.commit()
        conn.close()
        print("\nDatabase updated locally.")

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
