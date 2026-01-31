import ftplib
import os
import sqlite3

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
REMOTE_DB_PATH = '/httpdocs/backend/data/sdg_desktop.sqlite'
LOCAL_TEMP_DB = 'c:/SDG/temp_diagnose/remote_sdg_desktop.sqlite'

def check_db(db_path):
    print(f"\nChecking database: {db_path}")
    if not os.path.exists(db_path):
        print("Database file does not exist.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Found {len(tables)} tables.")
        
        critical_tables = [
            'users', 'companies', 'reports', 'data_points', 
            'sdg_goals', 'gri_standards', 'modules'
        ]
        
        for t in critical_tables:
            if t in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {t}")
                count = cursor.fetchone()[0]
                print(f"[OK] Table '{t}' exists ({count} rows).")
            else:
                print(f"[MISSING] Table '{t}' does not exist!")
                
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")

def main():
    if not os.path.exists('c:/SDG/temp_diagnose'):
        os.makedirs('c:/SDG/temp_diagnose')

    print(f"Connecting to FTP {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")
        
        print(f"Downloading {REMOTE_DB_PATH}...")
        with open(LOCAL_TEMP_DB, 'wb') as f:
            ftp.retrbinary(f'RETR {REMOTE_DB_PATH}', f.write)
        print("Download complete.")
        
        ftp.quit()
        
        check_db(LOCAL_TEMP_DB)
        
    except Exception as e:
        print(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
