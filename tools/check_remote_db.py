import sqlite3
import os
import ftplib

# FTP Bilgileri
FTP_HOST = "72.62.150.207"
FTP_USER = "cursorsustainageftp"
FTP_PASS = "Kayra_1507_Sk!"
REMOTE_DB_PATH = "/httpdocs/backend/data/sdg_desktop.sqlite"
LOCAL_TEMP_DB = "c:/SDG/temp_diagnose/remote_db_check.sqlite"

def ensure_dir(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

def check_db():
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
            ftp.quit()
            return

        ftp.quit()

        if not os.path.exists(LOCAL_TEMP_DB):
            print(f"Database not found at {LOCAL_TEMP_DB}")
            return

        conn = sqlite3.connect(LOCAL_TEMP_DB)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Found {len(tables)} tables.")
        
        table_names = [t[0] for t in tables]
        
        # Extended list of critical tables
        critical_tables = [
            'users', 'companies', 'reports', 'data_points', 
            'sdg_goals', 'gri_standards', 'modules', 'company_modules',
            'esg_scores', 'carbon_footprint',
            'esrs_standards', 'sasb_standards', 'tcfd_recommendations', 'tnfd_recommendations',
    'carbon_emissions', 'energy_consumption', 'water_consumption', 'waste_generation', 'waste_recycling', 'waste_records',
    'report_registry'
]
        
        for t in critical_tables:
            if t in table_names:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    count = cursor.fetchone()[0]
                    print(f"[OK] Table '{t}' exists ({count} rows).")
                    
                    if count > 0 and t == 'modules':
                         cursor.execute(f"SELECT * FROM {t} LIMIT 5")
                         rows = cursor.fetchall()
                         print(f"   Sample modules: {rows}")
                    
                    if count > 0 and t == 'company_modules':
                         cursor.execute(f"SELECT * FROM {t} LIMIT 5")
                         rows = cursor.fetchall()
                         print(f"   Sample company_modules: {rows}")

                except Exception as e:
                    print(f"[ERROR] Could not read table '{t}': {e}")
            else:
                print(f"[MISSING] Table '{t}' does not exist!")
                
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == '__main__':
    check_db()
