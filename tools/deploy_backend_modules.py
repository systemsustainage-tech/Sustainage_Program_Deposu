import os
import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs/backend/modules'
LOCAL_DIR = 'c:/SDG/server/backend/modules'

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
            if file.endswith('.pyc') or file.endswith('.log') or file.endswith('.sqlite') or file.endswith('.db'):
                continue
            
            l_file = os.path.join(root, file)
            r_file = f"{remote_path}/{file}"
            upload_file(ftp, l_file, r_file)

def main():
    ftp = connect_ftp()
    
    # Ensure base dir exists
    ensure_remote_dir(ftp, FTP_REMOTE_DIR)
    
    upload_recursive(ftp, LOCAL_DIR, FTP_REMOTE_DIR)
    
    # Also touch web_app.py to restart app if needed (re-upload)
    logging.info("Touching web_app.py...")
    ftp.cwd('/httpdocs')
    with open('c:/SDG/server/web_app.py', 'rb') as f:
        ftp.storbinary('STOR web_app.py', f)
        
    ftp.quit()
    logging.info("Modules deployment complete.")

if __name__ == '__main__':
    main()
