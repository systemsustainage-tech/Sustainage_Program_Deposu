import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs/logs'

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        try:
            ftp.mkd(FTP_REMOTE_DIR)
            logging.info(f"Created {FTP_REMOTE_DIR}")
        except ftplib.error_perm:
            logging.info(f"Directory {FTP_REMOTE_DIR} likely exists")
            
        try:
            ftp.voidcmd(f'SITE CHMOD 777 {FTP_REMOTE_DIR}')
            logging.info(f"Set permissions 777 for {FTP_REMOTE_DIR}")
        except:
            logging.warning("Could not set permissions")
            
        ftp.quit()
        
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
