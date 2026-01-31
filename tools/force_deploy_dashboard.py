import ftplib
import logging
import sys
import os

# Configure logging to print to stdout immediately
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    stream=sys.stdout
)

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

FILES_TO_UPLOAD = [
    ('c:/SDG/server/templates/dashboard.html', '/httpdocs/templates/dashboard.html'),
    ('c:/SDG/server/templates/base.html', '/httpdocs/templates/base.html'),
    ('c:/SDG/server/templates/sidebar.html', '/httpdocs/templates/sidebar.html'),
    ('c:/SDG/server/templates/navbar.html', '/httpdocs/templates/navbar.html'),
]

def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def main():
    ftp = connect_ftp()
    
    for local_path, remote_path in FILES_TO_UPLOAD:
        if os.path.exists(local_path):
            try:
                logging.info(f"Uploading {local_path} to {remote_path}...")
                with open(local_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_path}', f)
                logging.info(f"Successfully uploaded {remote_path}")
            except Exception as e:
                logging.error(f"Failed to upload {remote_path}: {e}")
        else:
            logging.warning(f"Local file not found: {local_path}")

    # Restart app by touching web_app.py
    try:
        logging.info("Touching web_app.py to restart application...")
        ftp.sendcmd('SITE CHMOD 755 /httpdocs/web_app.py')
    except Exception as e:
        logging.warning(f"Could not touch web_app.py: {e}")

    ftp.quit()

if __name__ == '__main__':
    main()
