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

def connect_ftp():
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp

def main():
    ftp = connect_ftp()
    
    # 1. Rename index.php to disable it
    try:
        logging.info("Renaming /httpdocs/index.php to /httpdocs/index.php.bak...")
        ftp.rename('/httpdocs/index.php', '/httpdocs/index.php.bak')
        logging.info("Successfully disabled index.php")
    except Exception as e:
        logging.warning(f"Could not rename index.php (might not exist or already renamed): {e}")

    # 2. Upload .htaccess
    try:
        logging.info("Uploading .htaccess...")
        with open('c:/SDG/server/.htaccess', 'rb') as f:
            ftp.storbinary('STOR /httpdocs/.htaccess', f)
        logging.info("Uploaded .htaccess")
    except Exception as e:
        logging.error(f"Failed to upload .htaccess: {e}")

    # 3. Upload updated wsgi.py
    try:
        logging.info("Uploading wsgi.py...")
        with open('c:/SDG/server/wsgi.py', 'rb') as f:
            ftp.storbinary('STOR /httpdocs/wsgi.py', f)
        logging.info("Uploaded wsgi.py")
    except Exception as e:
        logging.error(f"Failed to upload wsgi.py: {e}")

    # 4. Modify web_app.py to use CGIHandler if executed directly (fallback)
    # We won't modify web_app.py locally, but we might need to ensure it has the right permissions
    try:
        ftp.sendcmd('SITE CHMOD 755 /httpdocs/web_app.py')
        logging.info("Set permissions on web_app.py")
    except:
        pass

    ftp.quit()

if __name__ == '__main__':
    main()
