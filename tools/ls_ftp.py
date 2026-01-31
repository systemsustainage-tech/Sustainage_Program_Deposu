
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
        
        files = []
        ftp.dir(files.append)
        
        logging.info("Directory listing of /:")
        for f in files:
            print(f)
            
        # Check inside public_html
        if any('public_html' in f for f in files):
            logging.info("\nDirectory listing of /public_html:")
            files_pub = []
            ftp.cwd('/public_html')
            ftp.dir(files_pub.append)
            for f in files_pub:
                print(f)
                
        ftp.quit()
        
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
