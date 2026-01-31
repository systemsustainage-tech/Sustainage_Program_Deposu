
import ftplib
import os
import logging
import requests
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
REMOTE_DIR = '/httpdocs'

def main():
    try:
        # 1. Upload a test file
        filename = 'deploy_test.txt'
        content = 'Deployment Path Verification: SUCCESS'
        
        logging.info(f"Connecting to FTP...")
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        
        logging.info(f"Uploading {filename} to {REMOTE_DIR}/{filename}...")
        with open(filename, 'w') as f:
            f.write(content)
            
        with open(filename, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_DIR}/{filename}', f)
            
        # 2. Try to clean __pycache__
        logging.info("Attempting to remove __pycache__ directories...")
        try:
            # Simple recursive deletion of __pycache__ folders is hard via FTP
            # We can try to delete specific known ones or just rename them
            # For now, let's just try to list them to see if they exist
            files = ftp.nlst(REMOTE_DIR)
            if '__pycache__' in files:
                logging.info("Found __pycache__ in root. Trying to rename/delete...")
                try:
                    # Try rename to invalidate
                    ftp.rename(f'{REMOTE_DIR}/__pycache__', f'{REMOTE_DIR}/__pycache__old_{os.getpid()}')
                    logging.info("Renamed __pycache__")
                except Exception as e:
                    logging.warning(f"Could not rename __pycache__: {e}")
        except Exception as e:
            logging.warning(f"Error checking pycache: {e}")
            
        ftp.quit()
        
        # 3. Verify via HTTP
        url = f'https://sustainage.cloud/{filename}'
        logging.info(f"Verifying via HTTP: {url}")
        resp = requests.get(url)
        if resp.status_code == 200 and content in resp.text:
            logging.info("SUCCESS: File uploaded and accessible. Deployment path is correct.")
        else:
            logging.error(f"FAILURE: Could not access file. Status: {resp.status_code}, Content: {resp.text[:100]}")
            
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
