import os
import ftplib
import logging
import sys
from datetime import datetime

# Configure logging to print to stdout immediately
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    stream=sys.stdout
)

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

FILES_TO_CHECK = [
    '/httpdocs/templates/dashboard.html',
    '/httpdocs/web_app.py'
]

DOWNLOAD_DIR = 'c:/SDG/temp_diagnose'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def inspect_files(ftp):
    logging.info("Inspecting remote files...")
    
    # List root httpdocs to see structure
    logging.info("--- Listing /httpdocs ---")
    try:
        ftp.cwd('/httpdocs')
        ftp.retrlines('LIST')
    except Exception as e:
        logging.error(f"Failed to list /httpdocs: {e}")

    # Check specific files
    for remote_path in FILES_TO_CHECK:
        logging.info(f"--- Checking {remote_path} ---")
        try:
            # Get size and modification time (if supported)
            try:
                size = ftp.size(remote_path)
                logging.info(f"Size: {size} bytes")
            except:
                logging.info("Size: Unknown")
                
            try:
                mdtm = ftp.voidcmd(f"MDTM {remote_path}")
                logging.info(f"MDTM: {mdtm}")
            except:
                logging.info("MDTM: Not supported")

            # Download for content verification
            local_filename = os.path.basename(remote_path)
            local_path = os.path.join(DOWNLOAD_DIR, local_filename)
            
            with open(local_path, 'wb') as f:
                ftp.retrbinary(f"RETR {remote_path}", f.write)
            
            logging.info(f"Downloaded to {local_path}")
            
            # Print first few lines of downloaded file
            with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                head = f.read(200)
                logging.info(f"Content Head:\n{head}")

        except Exception as e:
            logging.error(f"Failed to check/download {remote_path}: {e}")

def main():
    try:
        ftp = connect_ftp()
        inspect_files(ftp)
        ftp.quit()
    except Exception as e:
        logging.error(f"Connection failed: {e}")

if __name__ == '__main__':
    main()
