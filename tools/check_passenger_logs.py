
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
        files = []
        ftp.dir(files.append)
        
        has_passenger = any('passenger_wsgi.py' in f for f in files)
        logging.info(f"Has passenger_wsgi.py: {has_passenger}")
        
        if has_passenger:
            logging.info("Passenger detected. Attempting restart...")
            try:
                if 'tmp' not in [f.split()[-1] for f in files]:
                    ftp.mkd('tmp')
                
                with open('restart.txt', 'w') as f:
                    f.write('restart')
                
                with open('restart.txt', 'rb') as f:
                    ftp.storbinary('STOR tmp/restart.txt', f)
                logging.info("Created tmp/restart.txt")
            except Exception as e:
                logging.error(f"Restart failed: {e}")
                
        # Check logs
        try:
            ftp.cwd('logs')
            log_files = []
            ftp.dir(log_files.append)
            logging.info("Logs directory content:")
            for f in log_files:
                print(f)
                
            # Try to download web_app.log
            if any('web_app.log' in f for f in log_files):
                logging.info("Downloading web_app.log...")
                with open('downloaded_web_app.log', 'wb') as f:
                    ftp.retrbinary('RETR web_app.log', f.write)
                
                with open('downloaded_web_app.log', 'r') as f:
                    print("--- Log Content ---")
                    print(f.read())
                    print("--- End Log ---")
        except Exception as e:
            logging.warning(f"Could not check logs: {e}")

        ftp.quit()
        
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
