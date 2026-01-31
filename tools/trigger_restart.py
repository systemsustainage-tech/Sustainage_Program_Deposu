
import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        ftp.cwd('/httpdocs')
        
        # Ensure tmp exists
        try:
            ftp.mkd('tmp')
            logging.info("Created tmp directory")
        except:
            logging.info("tmp directory likely exists")
            
        # Create restart.txt
        with open('restart.txt', 'w') as f:
            f.write('restart')
            
        logging.info("Uploading restart.txt...")
        with open('restart.txt', 'rb') as f:
            ftp.storbinary('STOR tmp/restart.txt', f)
            
        logging.info("Restart trigger uploaded.")
        ftp.quit()
        
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
