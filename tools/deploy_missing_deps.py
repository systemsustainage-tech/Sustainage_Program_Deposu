import os
import ftplib
import logging
import sys

# Configure logging to print to stdout immediately
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    stream=sys.stdout
)

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs'

def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def upload_recursive(ftp, local_path, remote_path):
    if not os.path.exists(local_path):
        logging.warning(f"Local path does not exist: {local_path}")
        return

    if os.path.isfile(local_path):
        try:
            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)
            logging.info(f"Uploaded file: {remote_path}")
        except Exception as e:
            logging.error(f"Failed to upload {remote_path}: {e}")
    elif os.path.isdir(local_path):
        try:
            ftp.mkd(remote_path)
            logging.info(f"Created directory: {remote_path}")
        except Exception:
            pass # Directory likely exists

        for item in os.listdir(local_path):
            if item == '__pycache__' or item.startswith('.'):
                continue
            
            local_item = os.path.join(local_path, item)
            remote_item = f"{remote_path}/{item}"
            upload_recursive(ftp, local_item, remote_item)

def main():
    ftp = connect_ftp()
    
    # Upload utils
    logging.info("Uploading utils...")
    upload_recursive(ftp, 'c:/SDG/server/utils', '/httpdocs/utils')
    
    # Upload services
    logging.info("Uploading services...")
    upload_recursive(ftp, 'c:/SDG/server/services', '/httpdocs/services')
    
    # Touch web_app.py to restart
    logging.info("Touching web_app.py to restart...")
    try:
        ftp.voidcmd('SITE CHMOD 755 /httpdocs/web_app.py')
    except:
        pass
        
    ftp.quit()
    logging.info("Deployment of missing dependencies complete.")

if __name__ == '__main__':
    main()
