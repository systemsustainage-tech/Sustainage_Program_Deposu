import os
import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs'
LOCAL_DIR = 'c:/SDG/server'

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
        # Filter directories
        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git', 'venv'}]
        
        rel_path = os.path.relpath(root, local_path).replace('\\', '/')
        if rel_path == '.':
            remote_path = remote_base
        else:
            remote_path = f"{remote_base}/{rel_path}"
            
        # Ensure remote dir exists
        try:
            ftp.mkd(remote_path)
        except:
            pass # Directory likely exists
        
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
    try:
        with open('temp_htaccess', 'w') as f:
            f.write(htaccess_content)
        with open('temp_htaccess', 'rb') as f:
            ftp.storbinary(f'STOR {FTP_REMOTE_DIR}/.htaccess', f)
        os.remove('temp_htaccess')
        logging.info("Uploaded .htaccess")
    except Exception as e:
        logging.error(f"Failed to create .htaccess: {e}")

def set_permissions(ftp, filename):
    try:
        ftp.voidcmd(f'SITE CHMOD 755 {FTP_REMOTE_DIR}/{filename}')
        logging.info(f"Set permissions 755 for {filename}")
    except Exception as e:
        logging.warning(f"Could not set permissions for {filename}: {e}")

def main():
    ftp = connect_ftp()
    if not ftp: return
    
    # 1. Upload web_app.py (Patched)
    upload_file(ftp, os.path.join(LOCAL_DIR, 'web_app.py'), f'{FTP_REMOTE_DIR}/web_app.py')
    set_permissions(ftp, 'web_app.py')
    
    # 2. Upload .htaccess
    create_htaccess(ftp)
    
    # 3. Upload utils and services (Dependencies)
    logging.info("Uploading utils...")
    upload_recursive(ftp, os.path.join(LOCAL_DIR, 'utils'), f'{FTP_REMOTE_DIR}/utils')
    
    logging.info("Uploading services...")
    upload_recursive(ftp, os.path.join(LOCAL_DIR, 'services'), f'{FTP_REMOTE_DIR}/services')
    
    ftp.quit()
    logging.info("Deployment Complete")

if __name__ == '__main__':
    main()
