import os
import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs'

EXCLUDE_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.git'}
EXCLUDE_DIRS = {'__pycache__', '.git', 'venv'}

def connect_ftp():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        return ftp
    except Exception as e:
        logging.error(f"FTP Connection Failed: {e}")
        return None

def upload_file(ftp, local_path, remote_path):
    try:
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_path}', f)
        logging.info(f"Uploaded: {remote_path}")
    except Exception as e:
        logging.error(f"Failed to upload {remote_path}: {e}")

def upload_recursive(ftp, local_path, remote_base):
    if not os.path.exists(local_path):
        logging.warning(f"Local path does not exist: {local_path}")
        return

    for root, dirs, files in os.walk(local_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        rel_path = os.path.relpath(root, local_path).replace('\\', '/')
        if rel_path == '.':
            remote_path = remote_base
        else:
            remote_path = f"{remote_base}/{rel_path}"
            
        try:
            ftp.mkd(remote_path)
        except:
            pass 
        
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in EXCLUDE_EXTENSIONS:
                continue
            
            # Exclude GUI files
            if file.endswith('_gui.py') or file == 'gui.py':
                logging.info(f"Skipping GUI file: {file}")
                continue
            
            l_file = os.path.join(root, file)
            r_file = f"{remote_path}/{file}"
            upload_file(ftp, l_file, r_file)

def main():
    ftp = connect_ftp()
    if not ftp: return
    
    # Upload config
    logging.info("Uploading config...")
    upload_recursive(ftp, 'c:/SDG/config', f'{FTP_REMOTE_DIR}/config')
    
    # Upload tasks
    logging.info("Uploading tasks...")
    upload_recursive(ftp, 'c:/SDG/tasks', f'{FTP_REMOTE_DIR}/tasks')
    
    # Ensure data/sessions exists
    try:
        ftp.mkd(f'{FTP_REMOTE_DIR}/data')
    except:
        pass
    try:
        ftp.mkd(f'{FTP_REMOTE_DIR}/data/sessions')
        # Try to set permissions if possible (might not work on all FTPs)
        ftp.voidcmd(f'SITE CHMOD 777 {FTP_REMOTE_DIR}/data/sessions')
    except:
        pass

    ftp.quit()
    logging.info("Core dependencies deployment complete")

if __name__ == '__main__':
    main()
