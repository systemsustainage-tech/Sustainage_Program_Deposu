import os
import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs'
LOCAL_DIR = 'c:/SDG/server'

EXCLUDE_DIRS = {'__pycache__', 'venv', '.git', 'data', 'company_logos'} # Exclude data for speed

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
        # Filter directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        rel_path = os.path.relpath(root, local_path).replace('\\', '/')
        if rel_path == '.':
            remote_path = remote_base
        else:
            remote_path = f"{remote_base}/{rel_path}"
            
        # Ensure remote dir exists (optimization: only if not root)
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

def create_htaccess(ftp):
    htaccess_content = """# Python CGI
Options +ExecCGI
AddHandler cgi-script .py

<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^(.*)$ /web_app.py/$1 [QSA,L]
</IfModule>

<FilesMatch "\\.(db|sqlite|log)$">
    Order allow,deny
    Deny from all
</FilesMatch>
"""
    with open('temp_htaccess', 'w') as f:
        f.write(htaccess_content)
    with open('temp_htaccess', 'rb') as f:
        ftp.storbinary(f'STOR {FTP_REMOTE_DIR}/.htaccess', f)
    os.remove('temp_htaccess')
    logging.info("Uploaded .htaccess")

def main():
    ftp = connect_ftp()
    
    # Upload web_app.py
    upload_file(ftp, os.path.join(LOCAL_DIR, 'web_app.py'), f'{FTP_REMOTE_DIR}/web_app.py')
    
    # Upload directories
    for folder in ['templates', 'static', 'backend']:
        local_folder = os.path.join(LOCAL_DIR, folder)
        if os.path.exists(local_folder):
            upload_recursive(ftp, local_folder, f'{FTP_REMOTE_DIR}/{folder}')
            
    create_htaccess(ftp)
    ftp.quit()
    logging.info("Deployment complete.")

if __name__ == '__main__':
    main()
