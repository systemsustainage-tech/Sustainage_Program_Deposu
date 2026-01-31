import sqlite3
import os
import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
REMOTE_DB_PATH = '/httpdocs/backend/data/sdg_desktop.sqlite'
LOCAL_DB_PATH = 'temp_remote_waste.sqlite'

def download_db():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        with open(LOCAL_DB_PATH, 'wb') as f:
            ftp.retrbinary(f'RETR {REMOTE_DB_PATH}', f.write)
        
        logging.info("Database downloaded")
        ftp.quit()
        return True
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return False

def check_waste_tables():
    if not os.path.exists(LOCAL_DB_PATH):
        return
        
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    tables = ['waste_generation', 'waste_recycling']
    
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cursor.fetchone():
            logging.info(f"Table '{table}' exists.")
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [info[1] for info in cursor.fetchall()]
            logging.info(f"  Columns: {columns}")
            
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logging.info(f"  Row count: {count}")
        else:
            logging.error(f"Table '{table}' MISSING!")

    conn.close()
    os.remove(LOCAL_DB_PATH)

if __name__ == '__main__':
    if download_db():
        check_waste_tables()
