import ftplib
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

LOCAL_DB_PATH = 'c:/SDG/server/backend/data/sdg_desktop.sqlite'
REMOTE_DB_DIR = '/httpdocs/backend/data'
REMOTE_DB_PATH = '/httpdocs/backend/data/sdg_desktop.sqlite'

def main():
    if not os.path.exists(LOCAL_DB_PATH):
        logging.error(f"Local DB not found at {LOCAL_DB_PATH}")
        return

    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        # Ensure directories exist
        dirs = REMOTE_DB_DIR.split('/')
        path = ""
        for d in dirs:
            if not d: continue
            path += "/" + d
            try:
                ftp.mkd(path)
                logging.info(f"Created directory: {path}")
            except:
                pass
        
        # Upload DB
        logging.info(f"Uploading {LOCAL_DB_PATH} to {REMOTE_DB_PATH}...")
        with open(LOCAL_DB_PATH, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_DB_PATH}', f)
        logging.info("Upload complete.")
        
        # Set permissions
        try:
            ftp.voidcmd(f'SITE CHMOD 777 {REMOTE_DB_PATH}') # Writable by web server
            logging.info(f"Set permissions 777 for {REMOTE_DB_PATH}")
        except:
            logging.warning("Could not set permissions for DB file")
            
        try:
            ftp.voidcmd(f'SITE CHMOD 777 {REMOTE_DB_DIR}') # Directory also writable
            logging.info(f"Set permissions 777 for {REMOTE_DB_DIR}")
        except:
            logging.warning("Could not set permissions for DB dir")
            
        ftp.quit()
        
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
