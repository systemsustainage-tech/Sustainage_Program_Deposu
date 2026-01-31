
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
        
        ftp.cwd('/httpdocs/KAYRA_KEREM')
        files = []
        ftp.dir(files.append)
        for f in files:
            print(f)
            
        logging.info("Checking /httpdocs/eskiweb")
        ftp.cwd('/httpdocs/eskiweb')
        files = []
        ftp.dir(files.append)
        for f in files:
            print(f)
            
        ftp.quit()
        
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
