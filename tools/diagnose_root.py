import ftplib
import logging
import sys

# Configure logging to print to stdout immediately
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    stream=sys.stdout
)

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info(f"Connected to {FTP_HOST}")
        
        logging.info("Listing ROOT / ...")
        files = ftp.nlst('/')
        logging.info(f"Files in /: {files}")
        
        logging.info("Listing /httpdocs/backend ...")
        try:
            files_backend = ftp.nlst('/httpdocs/backend')
            logging.info(f"Files in /httpdocs/backend: {files_backend}")
        except Exception as e:
            logging.error(f"Failed to list /httpdocs/backend: {e}")

        # Check for logs in root
        # Handle absolute paths in listing
        logs_path = next((f for f in files if f.endswith('/logs') or f == 'logs'), None)
        
        if logs_path:
            logging.info(f"Checking {logs_path} directory...")
            try:
                logs = ftp.nlst(logs_path)
                logging.info(f"Files in {logs_path}: {logs}")
                
                # Try to read error_log if present
                for log in logs:
                    if 'error' in log:
                        logging.info(f"Downloading last 2KB of {log}...")
                        from io import BytesIO
                        bio = BytesIO()
                        # log might be absolute or relative depending on server
                        # ftp.nlst usually returns same format as input or relative names
                        # Safe to try retrieving as is if it looks absolute, or join if relative
                        remote_log_path = log if log.startswith('/') else f"{logs_path}/{log}"
                        
                        try:
                            ftp.retrbinary(f'RETR {remote_log_path}', bio.write)
                            content = bio.getvalue().decode('utf-8', errors='ignore')
                            lines = content.splitlines()
                            logging.info(f"--- TAIL of {remote_log_path} ---")
                            for line in lines[-20:]:
                                logging.info(line)
                            logging.info("-------------------------")
                        except Exception as e:
                            logging.error(f"Failed to read {remote_log_path}: {e}")
            except Exception as e:
                logging.error(f"Failed to check logs: {e}")

        ftp.quit()
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
