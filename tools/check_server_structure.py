import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        
        logging.info("Listing /httpdocs:")
        ftp.cwd('/httpdocs')
        ftp.retrlines('LIST')
        
        logging.info("\nListing /httpdocs/backend:")
        try:
            ftp.cwd('/httpdocs/backend')
            ftp.retrlines('LIST')
        except:
            logging.info("backend dir not found")

        logging.info("\nListing /httpdocs/yonetim:")
        try:
            ftp.cwd('/httpdocs/yonetim')
            ftp.retrlines('LIST')
        except:
            logging.info("yonetim dir not found")
            
        ftp.quit()
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
