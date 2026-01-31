import ftplib
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

LOCAL_FILE = 'c:/SDG/server/web_app.py'
REMOTE_FILE = '/httpdocs/app_v2.py'

HTACCESS_CONTENT = """Options +ExecCGI
AddHandler cgi-script .py .cgi
DirectoryIndex app_v2.py index.php index.html

RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ app_v2.py/$1 [L]
"""

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        # Upload app_v2.py
        logging.info(f"Uploading {LOCAL_FILE} as {REMOTE_FILE}...")
        with open(LOCAL_FILE, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_FILE}', f)
        
        # Set permissions
        try:
            ftp.voidcmd(f'SITE CHMOD 755 {REMOTE_FILE}')
            logging.info(f"Set permissions for {REMOTE_FILE}")
        except:
            logging.warning("Could not set permissions")
            
        # Upload .htaccess
        logging.info("Uploading .htaccess...")
        with open('temp_htaccess_v2', 'w') as f:
            f.write(HTACCESS_CONTENT)
            
        with open('temp_htaccess_v2', 'rb') as f:
            ftp.storbinary('STOR /httpdocs/.htaccess', f)
            
        logging.info("Deployment Complete")
        ftp.quit()
        
        if os.path.exists('temp_htaccess_v2'):
            os.remove('temp_htaccess_v2')
            
    except Exception as e:
        logging.error(f"Deployment failed: {e}")

if __name__ == '__main__':
    main()
