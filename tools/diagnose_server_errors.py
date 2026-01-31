import ftplib
import logging
import sys
import os

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
        
        logging.info("Listing /httpdocs...")
        ftp.cwd('/httpdocs')
        files = ftp.nlst()
        logging.info(f"Files in /httpdocs: {files}")
        
        # Check for error logs
        log_files = [f for f in files if 'log' in f or 'err' in f]
        logging.info(f"Potential log files: {log_files}")

        # Check for logs directory
        try:
            ftp.cwd('/httpdocs/logs')
            log_files_in_dir = ftp.nlst()
            logging.info(f"Files in /httpdocs/logs: {log_files_in_dir}")
            for lf in log_files_in_dir:
                if 'web_app.log' in lf or 'error' in lf:
                    logging.info(f"Downloading last 2KB of logs/{lf}...")
                    bio = BytesIO()
                    ftp.retrbinary(f'RETR {lf}', bio.write)
                    content = bio.getvalue().decode('utf-8', errors='ignore')
                    lines = content.splitlines()
                    logging.info(f"--- TAIL of logs/{lf} ---")
                    for line in lines[-20:]:
                        logging.info(line)
                    logging.info("-------------------------")
            ftp.cwd('/httpdocs')
        except Exception as e:
            logging.info(f"Could not check /httpdocs/logs: {e}")
            ftp.cwd('/httpdocs')
        
        for log_file in log_files:
            if log_file == 'error_log':
                logging.info(f"Downloading last 2KB of {log_file}...")
                # Download into memory
                from io import BytesIO
                bio = BytesIO()
                try:
                    # Get size
                    size = ftp.size(log_file)
                    # Retrieve partial if supported, or full
                    # Standard FTP RETR doesn't support offset easily without REST, but let's try reading full and tailing
                    # If file is huge, this is bad. Let's try to just read it.
                    ftp.retrbinary(f'RETR {log_file}', bio.write)
                    content = bio.getvalue().decode('utf-8', errors='ignore')
                    lines = content.splitlines()
                    logging.info(f"--- TAIL of {log_file} ---")
                    for line in lines[-20:]:
                        logging.info(line)
                    logging.info("-------------------------")
                except Exception as e:
                    logging.error(f"Failed to read {log_file}: {e}")

        # Check if utils and services folders exist
        logging.info("Checking for utils and services folders...")
        try:
            utils_list = ftp.nlst('utils')
            logging.info(f"utils folder exists: {utils_list}")
        except:
            logging.info("utils folder MISSING")
            
        try:
            services_list = ftp.nlst('services')
            logging.info(f"services folder exists: {services_list}")
        except:
            logging.info("services folder MISSING")

        ftp.quit()
    except Exception as e:
        logging.error(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
