import sqlite3
import os
import ftplib
import traceback

# FTP Bilgileri
FTP_HOST = "72.62.150.207"
FTP_USER = "cursorsustainageftp"
FTP_PASS = "Kayra_1507_Sk!"
REMOTE_DB_PATH = "/httpdocs/backend/data/sdg_desktop.sqlite"
LOCAL_TEMP_DIR = "c:/SDG/temp_diagnose"
LOCAL_TEMP_DB = os.path.join(LOCAL_TEMP_DIR, "remote_db_patch_tables.sqlite")

def ensure_dir(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

def create_missing_tables(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Creating 'reports' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
          id INTEGER PRIMARY KEY,
          company_id INTEGER NOT NULL,
          type TEXT NOT NULL,
          period TEXT NOT NULL,
          payload_json TEXT,
          file_path TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        )
    """)
    
    print("Creating 'data_points' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            module TEXT NOT NULL,
            indicator_code TEXT,
            value REAL,
            unit TEXT,
            year INTEGER,
            period TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        )
    """)

    print("Creating 'esg_scores' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS esg_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            score REAL,
            environment_score REAL,
            social_score REAL,
            governance_score REAL,
            period TEXT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        )
    """)

    print("Creating 'carbon_footprint' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carbon_footprint (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            scope1 REAL,
            scope2 REAL,
            scope3 REAL,
            total_emissions REAL,
            unit TEXT DEFAULT 'tCO2e',
            period TEXT,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        )
    """)

    print("Creating 'sasb_standards' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sasb_standards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            sector TEXT,
            topic TEXT,
            metric TEXT,
            unit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("Creating 'tcfd_recommendations' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tcfd_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pillar TEXT NOT NULL, -- Governance, Strategy, Risk Management, Metrics & Targets
            recommendation TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("Creating 'tnfd_recommendations' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tnfd_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pillar TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("Creating 'esrs_standards' table (if not exists)...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS esrs_standards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            title TEXT,
            category TEXT,
            description TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def main():
    ensure_dir(LOCAL_TEMP_DB)
    
    print(f"Connecting to FTP {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")
        
        print(f"Downloading {REMOTE_DB_PATH}...")
        try:
            with open(LOCAL_TEMP_DB, 'wb') as f:
                ftp.retrbinary(f'RETR {REMOTE_DB_PATH}', f.write)
            print("Download complete.")
        except Exception as e:
            print(f"Download failed: {e}")
            # If download fails, maybe the file doesn't exist? 
            # But we know it exists from previous checks.
            # We will proceed only if download succeeded.
            ftp.quit()
            return

        create_missing_tables(LOCAL_TEMP_DB)
        
        print(f"Uploading patched DB back to {REMOTE_DB_PATH}...")
        with open(LOCAL_TEMP_DB, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_DB_PATH}', f)
        print("Upload complete.")
        
        ftp.quit()
        print("\nSUCCESS: Remote database patched with missing tables.")
        
    except Exception as e:
        print(f"FTP/Processing Error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
