import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

def list_files(ftp, path):
    try:
        logging.info(f"Listing {path}...")
        ftp.cwd(path)
        ftp.retrlines('LIST')
    except Exception as e:
        logging.error(f"Error listing {path}: {e}")

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        list_files(ftp, '/httpdocs')
        list_files(ftp, '/httpdocs/backend')
        list_files(ftp, '/httpdocs/yonetim')
        
        ftp.quit()
        
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    main()
