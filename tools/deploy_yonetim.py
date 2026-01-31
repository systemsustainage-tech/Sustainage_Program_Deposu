import ftplib
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

LOCAL_DIR = 'c:/SDG/yonetim'
REMOTE_DIR = '/httpdocs/yonetim'

EXCLUDE_DIRS = {'__pycache__', '.git', 'venv'}

def upload_recursive(ftp, local_path, remote_path):
    try:
        ftp.mkd(remote_path)
        logging.info(f"Created directory: {remote_path}")
    except:
        pass
        
    for item in os.listdir(local_path):
        if item in EXCLUDE_DIRS:
            continue
            
        local_item_path = os.path.join(local_path, item)
        remote_item_path = f"{remote_path}/{item}"
        
        if os.path.isdir(local_item_path):
            upload_recursive(ftp, local_item_path, remote_item_path)
        else:
            try:
                with open(local_item_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_item_path}', f)
                logging.info(f"Uploaded: {item}")
            except Exception as e:
                logging.error(f"Failed to upload {item}: {e}")

def main():
    if not os.path.exists(LOCAL_DIR):
        logging.error(f"Local dir not found: {LOCAL_DIR}")
        return

    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        upload_recursive(ftp, LOCAL_DIR, REMOTE_DIR)
        
        ftp.quit()
        logging.info("Deployment complete.")
        
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
