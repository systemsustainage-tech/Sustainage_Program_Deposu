import ftplib
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

def download_and_check():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        with open('temp_remote_web_app.py', 'wb') as f:
            ftp.retrbinary('RETR /httpdocs/web_app.py', f.write)
        
        logging.info("Downloaded web_app.py")
        ftp.quit()
        
        with open('temp_remote_web_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'test_debug' in content:
                logging.info("SUCCESS: 'test_debug' route found in remote file.")
            else:
                logging.error("FAILURE: 'test_debug' route NOT found in remote file.")
                
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == '__main__':
    download_and_check()
