import ftplib
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
FTP_REMOTE_LOGS = '/httpdocs/logs'

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        try:
            ftp.cwd(FTP_REMOTE_LOGS)
            logging.info(f"Listing of {FTP_REMOTE_LOGS}:")
            files = []
            ftp.retrlines('LIST', files.append)
            
            cgitb_files = []
            for line in files:
                print(line)
                parts = line.split()
                filename = parts[-1]
                if filename.endswith('.html') or filename.endswith('.txt'):
                    cgitb_files.append(filename)
            
            if cgitb_files:
                # Download the latest one
                latest = cgitb_files[-1] # List usually sorted or we take last
                logging.info(f"Downloading latest log: {latest}")
                local_path = f"c:/SDG/server/logs/{latest}"
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {latest}', f.write)
                logging.info(f"Downloaded to {local_path}. Content preview:")
                with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                    print(f.read()[:2000]) # First 2000 chars
            else:
                logging.info("No cgitb log files found.")
                
        except ftplib.error_perm as e:
            logging.error(f"Could not access logs directory: {e}")
            
        ftp.quit()
        
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
