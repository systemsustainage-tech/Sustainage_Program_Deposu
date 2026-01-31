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
FTP_REMOTE_DIR = '/httpdocs/backend/modules'
LOCAL_DIR = 'c:/SDG/server/backend/modules'

# Priority modules to upload
MODULES_TO_UPLOAD = [
    'environmental',
    'social',
    'governance',
    'economic',
    'esg',
    'cbam',
    'csrd',
    'eu_taxonomy',
    'gri',
    'sdg',
    'cdp',
    'ifrs',
    'sasb',
    'reporting',
    'advanced_reporting',
    'scope3',
    'product_technology',
    'quality',
    'security',
    'innovation',
    'integration'
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
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
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
            if file.endswith('.pyc') or file.endswith('.log') or file.endswith('.sqlite') or file.endswith('.db') or file.endswith('.bak'):
                continue
            
            l_file = os.path.join(root, file)
            r_file = f"{remote_path}/{file}"
            upload_file(ftp, l_file, r_file)

def main():
    ftp = connect_ftp()
    
    # Upload selected modules
    for module in MODULES_TO_UPLOAD:
        local_mod_path = os.path.join(LOCAL_DIR, module)
        if os.path.exists(local_mod_path):
            logging.info(f"Uploading module: {module}")
            remote_mod_path = f"{FTP_REMOTE_DIR}/{module}"
            ensure_remote_dir(ftp, remote_mod_path)
            upload_recursive(ftp, local_mod_path, remote_mod_path)
        else:
            logging.warning(f"Module not found locally: {module}")
            
    # Touch web_app.py
    logging.info("Touching web_app.py...")
    ftp.cwd('/httpdocs')
    with open('c:/SDG/server/web_app.py', 'rb') as f:
        ftp.storbinary('STOR web_app.py', f)
        
    ftp.quit()
    logging.info("Core modules deployment complete.")

if __name__ == '__main__':
    main()
