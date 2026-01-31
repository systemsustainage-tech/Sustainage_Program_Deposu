import ftplib
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs'

def connect_ftp():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        return ftp
    except Exception as e:
        logging.error(f"FTP Connection failed: {e}")
        return None

def upload_file(ftp, local_path, remote_path):
    try:
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_path}', f)
        logging.info(f"Uploaded: {local_path} -> {remote_path}")
        
        # Set permissions for web_app.py
        if remote_path.endswith('.py') or remote_path.endswith('.cgi'):
             try:
                 ftp.voidcmd(f'SITE CHMOD 755 {remote_path}')
                 logging.info(f"Set permissions 755 for {remote_path}")
             except:
                 pass
                 
    except Exception as e:
        logging.error(f"Upload failed for {local_path}: {e}")

def main():
    ftp = connect_ftp()
    if not ftp: return
    
    # Upload web_app.py
    upload_file(ftp, 'c:/SDG/server/web_app.py', f'{FTP_REMOTE_DIR}/web_app.py')
    
    # Upload .htaccess (create temporary)
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
    upload_file(ftp, 'temp_htaccess', f'{FTP_REMOTE_DIR}/.htaccess')
    os.remove('temp_htaccess')
    
    ftp.quit()
    logging.info("Patch Deployment Complete")

if __name__ == '__main__':
    main()
