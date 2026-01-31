import os
import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

DIRS_TO_UPLOAD = ['config', 'utils', 'services']
LOCAL_BASE = 'c:/SDG'
REMOTE_BASE = '/httpdocs'

EXCLUDE_DIRS = {'__pycache__', '.git', 'venv'}

def upload_recursive(ftp, local_path, remote_path):
    try:
        ftp.mkd(remote_path)
        logging.info(f"Created directory: {remote_path}")
    except:
        pass
    
    for item in os.listdir(local_path):
        local_item_path = os.path.join(local_path, item)
        remote_item_path = f"{remote_path}/{item}"
        
        if os.path.isdir(local_item_path):
            if item not in EXCLUDE_DIRS:
                upload_recursive(ftp, local_item_path, remote_item_path)
        else:
            try:
                with open(local_item_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_item_path}', f)
                logging.info(f"Uploaded: {remote_item_path}")
                
                # Set permissions for Python files
                if item.endswith('.py'):
                    try:
                        ftp.voidcmd(f'SITE CHMOD 755 {remote_item_path}')
                    except:
                        pass
            except Exception as e:
                logging.error(f"Failed to upload {local_item_path}: {e}")

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        for dir_name in DIRS_TO_UPLOAD:
            local_dir = os.path.join(LOCAL_BASE, dir_name)
            remote_dir = f"{REMOTE_BASE}/{dir_name}"
            if os.path.exists(local_dir):
                logging.info(f"Uploading {dir_name}...")
                upload_recursive(ftp, local_dir, remote_dir)
            else:
                logging.warning(f"Local directory not found: {local_dir}")
        
        ftp.quit()
        logging.info("Deployment complete.")
        
    except Exception as e:
        logging.error(f"Deployment failed: {e}")

if __name__ == '__main__':
    main()
