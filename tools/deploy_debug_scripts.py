import ftplib
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

FILES_TO_UPLOAD = {
    'c:/SDG/server/test_import_debug.py': '/httpdocs/test_import_debug.py',
    'c:/SDG/server/test_cgi.py': '/httpdocs/test_cgi.py'
}

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        for local_path, remote_path in FILES_TO_UPLOAD.items():
            if os.path.exists(local_path):
                logging.info(f"Uploading {local_path} to {remote_path}...")
                with open(local_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_path}', f)
                
                try:
                    ftp.voidcmd(f'SITE CHMOD 755 {remote_path}')
                    logging.info(f"Set permissions for {remote_path}")
                except:
                    logging.warning(f"Could not set permissions for {remote_path}")
            else:
                logging.warning(f"File not found: {local_path}")
        
        ftp.quit()
        logging.info("Upload complete.")
        
    except Exception as e:
        logging.error(f"Upload failed: {e}")

if __name__ == '__main__':
    main()
