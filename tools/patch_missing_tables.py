import sqlite3
import ftplib
import os

FTP_HOST = "72.62.150.207"
FTP_USER = "cursorsustainageftp"
FTP_PASS = "Kayra_1507_Sk!"
REMOTE_DB_PATH = "/httpdocs/backend/data/sdg_desktop.sqlite"
LOCAL_TEMP_DB = "c:/SDG/temp_diagnose/patch_missing_tables.sqlite"

def ensure_dir(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

def patch_db():
    ensure_dir(LOCAL_TEMP_DB)
    
    # 1. Download DB
    print(f"Connecting to FTP {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")
        
        print(f"Downloading {REMOTE_DB_PATH}...")
        with open(LOCAL_TEMP_DB, 'wb') as f:
            ftp.retrbinary(f'RETR {REMOTE_DB_PATH}', f.write)
        print("Download complete.")
        
        # 2. Patch DB
        conn = sqlite3.connect(LOCAL_TEMP_DB)
        cursor = conn.cursor()
        
        print("Creating 'carbon_emissions' table...")
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
        
        print("Creating 'report_registry' table...")
        cursor.execute("""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create waste_generation table
        print("Creating 'waste_generation' table...")
        cursor.execute("DROP TABLE IF EXISTS waste_generation")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_generation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    waste_type TEXT NOT NULL,
                    waste_category TEXT NOT NULL,
                    waste_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    disposal_method TEXT,
                    disposal_cost REAL,
                    location TEXT,
                    hazardous_status TEXT,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

        # Create waste_recycling table
        print("Creating 'waste_recycling' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_recycling (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER,
                waste_type TEXT NOT NULL,
                recycled_amount REAL NOT NULL,
                unit TEXT NOT NULL,
                recycling_method TEXT,
                recycling_rate REAL,
                revenue REAL,
                location TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create waste_categories table
        print("Creating 'waste_categories' table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waste_type TEXT NOT NULL,
                category TEXT NOT NULL,
                hazardous TEXT,
                recycling_potential TEXT,
                disposal_method TEXT,
                environmental_impact TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert sample data if empty
        
        # Carbon Emissions Sample
        cursor.execute("SELECT COUNT(*) FROM carbon_emissions")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample data into carbon_emissions...")
            cursor.execute("""
                INSERT INTO carbon_emissions (company_id, period, scope, category, quantity, unit, co2e_emissions)
                VALUES (1, '2024-01', 'Scope 1', 'Doğalgaz', 1000, 'm3', 2.1)
            """)
            
        # Report Registry Sample
        cursor.execute("SELECT COUNT(*) FROM report_registry")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample data into report_registry...")
            cursor.execute("""
                INSERT INTO report_registry (company_id, module_code, report_name, report_type, reporting_period, description, created_by)
                VALUES (1, 'GRI', '2023 Sürdürülebilirlik Raporu', 'Yıllık', '2023', 'GRI Standartlarına uygun yıllık rapor', 1)
            """)

        # Waste Generation Sample
        cursor.execute("SELECT COUNT(*) FROM waste_generation")
        if cursor.fetchone()[0] == 0:
            print("Inserting sample data into waste_generation...")
            cursor.execute("""
                INSERT INTO waste_generation (company_id, period, waste_type, amount, unit, disposal_method)
                VALUES (1, '2024-01', 'Kağıt/Karton', 500, 'kg', 'Geri Dönüşüm')
            """)

        conn.commit()
        conn.close()
        print("Database patched locally.")
        
        # 3. Upload DB
        print(f"Uploading patched DB to {REMOTE_DB_PATH}...")
        with open(LOCAL_TEMP_DB, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_DB_PATH}', f)
        print("Upload complete.")
        
        ftp.quit()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    patch_db()
