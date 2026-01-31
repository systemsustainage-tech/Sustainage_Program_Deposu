import os
import ftplib
import logging
import sys
import glob

# Configure logging to print to stdout immediately
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    stream=sys.stdout
)

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
REMOTE_DB_PATH = '/httpdocs/backend/data/sdg_desktop.sqlite'
LOCAL_DATA_DIR = 'c:/SDG/server/backend/data'

def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def main():
    # Find latest .bak file
    pattern = os.path.join(LOCAL_DATA_DIR, 'sdg_desktop.sqlite.*.bak')
    files = glob.glob(pattern)
    
    if not files:
        logging.error("No backup files found in " + LOCAL_DATA_DIR)
        return

    # Sort by modification time (or name since it has timestamp)
    latest_file = max(files, key=os.path.getmtime)
    logging.info(f"Found latest backup: {latest_file}")
    
    ftp = connect_ftp()
    
    # Check if remote DB exists (optional, but good to know)
    # If we overwrite, we might lose new data, but since the user says "it's all wrong", 
    # restoring a known working state (from backup) is safer than an empty/broken DB.
    
    logging.info(f"Uploading {latest_file} to {REMOTE_DB_PATH}...")
    try:
        with open(latest_file, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_DB_PATH}', f)
        logging.info("Database restored successfully.")
    except Exception as e:
        logging.error(f"Failed to upload database: {e}")
    
    ftp.quit()

if __name__ == '__main__':
    main()
