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
FTP_REMOTE_BASE = '/httpdocs/backend'
LOCAL_BASE = 'c:/SDG/server/backend'

# Directories to upload (excluding modules which is already done)
DIRS_TO_UPLOAD = [
    'app',
    'carbon',
    'config',
    'core',
    'data',
    'locales'
]

def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def ensure_remote_dir(ftp, path):
    parts = path.split('/')
    for i in range(len(parts)):
        parent = '/'.join(parts[:i+1])
        if not parent: continue
        try:
            ftp.cwd(parent)
        except:
            try:
                ftp.mkd(parent)
            except:
                pass

def upload_file(ftp, local_path, remote_path):
    try:
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_path}', f)
        logging.info(f"Uploaded: {remote_path}")
    except Exception as e:
        logging.error(f"Failed to upload {remote_path}: {e}")

def upload_recursive(ftp, local_path, remote_base):
    for root, dirs, files in os.walk(local_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        rel_path = os.path.relpath(root, local_path).replace('\\', '/')
        if rel_path == '.':
            remote_path = remote_base
        else:
            remote_path = f"{remote_base}/{rel_path}"
            
        if rel_path != '.':
            try:
                ftp.cwd(remote_path)
            except:
                ensure_remote_dir(ftp, remote_path)
        
        for file in files:
            if file.startswith('.') or file.endswith('.pyc') or file.endswith('.log') or file.endswith('.sqlite') or file.endswith('.db'): 
                continue
            
            l_file = os.path.join(root, file)
            r_file = f"{remote_path}/{file}"
            upload_file(ftp, l_file, r_file)

def main():
    ftp = connect_ftp()
    
    # 1. Upload specific directories
    for d in DIRS_TO_UPLOAD:
        local_dir = os.path.join(LOCAL_BASE, d)
        remote_dir = f"{FTP_REMOTE_BASE}/{d}"
        if os.path.exists(local_dir):
            logging.info(f"Uploading directory: {d}...")
            ensure_remote_dir(ftp, remote_dir)
            upload_recursive(ftp, local_dir, remote_dir)
    
    # 2. Upload files in the root of backend/
    logging.info("Uploading root files in backend/...")
    ensure_remote_dir(ftp, FTP_REMOTE_BASE)
    for file in os.listdir(LOCAL_BASE):
        local_file = os.path.join(LOCAL_BASE, file)
        if os.path.isfile(local_file):
            if file.startswith('.') or file.endswith('.pyc'): continue
            remote_file = f"{FTP_REMOTE_BASE}/{file}"
            upload_file(ftp, local_file, remote_file)

    # Touch web_app.py
    logging.info("Touching web_app.py...")
    ftp.cwd('/httpdocs')
    with open('c:/SDG/server/web_app.py', 'rb') as f:
        ftp.storbinary('STOR web_app.py', f)
        
    ftp.quit()
    logging.info("Backend rest deployment complete.")

if __name__ == '__main__':
    main()
