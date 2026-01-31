import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_DIR = '/httpdocs'

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        with open('c:/SDG/server/test_cgi.py', 'rb') as f:
            ftp.storbinary(f'STOR {FTP_REMOTE_DIR}/test_cgi.py', f)
        logging.info("Uploaded test_cgi.py")
        
        try:
            ftp.voidcmd(f'SITE CHMOD 755 {FTP_REMOTE_DIR}/test_cgi.py')
            logging.info("Set permissions 755 for test_cgi.py")
        except:
            logging.warning("Could not set permissions")
            
        ftp.quit()
        
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
