import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs'

def fix_session_dir():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        # Create flask_session dir if not exists
        try:
            ftp.mkd(f'{FTP_REMOTE_DIR}/flask_session')
            logging.info("Created flask_session directory")
        except:
            logging.info("flask_session directory already exists")
            
        # Try to chmod 777
        try:
            ftp.voidcmd(f'SITE CHMOD 777 {FTP_REMOTE_DIR}/flask_session')
            logging.info("Set permissions 777 for flask_session")
        except Exception as e:
            logging.warning(f"Could not set permissions: {e}")
            
        ftp.quit()
        
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    fix_session_dir()
