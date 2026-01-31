
import ftplib
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'

def main():
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        logging.info("Connected to FTP")
        
        # 1. Rename web_app.py to web_app.py.bak
        logging.info("Renaming /httpdocs/web_app.py to /httpdocs/web_app.py.bak")
        try:
            ftp.rename('/httpdocs/web_app.py', '/httpdocs/web_app.py.bak')
        except Exception as e:
            logging.error(f"Rename failed: {e}")
            ftp.quit()
            return

        # 2. Check site
        try:
            logging.info("Checking site status...")
            resp = requests.get('https://sustainage.cloud/login')
            logging.info(f"Status: {resp.status_code}")
            if "UserManager" in resp.text:
                logging.info("SITE IS STILL WORKING! httpdocs is NOT the live directory (or heavy caching).")
            else:
                logging.info("Site behavior changed! (Likely 500 or 404). httpdocs IS the live directory.")
                logging.info(f"Response snippet: {resp.text[:200]}")
        except Exception as e:
            logging.error(f"Request failed: {e}")

        # 3. Rename back
        logging.info("Renaming back...")
        try:
            ftp.rename('/httpdocs/web_app.py.bak', '/httpdocs/web_app.py')
        except Exception as e:
            logging.error(f"Rename back failed: {e}")
            
        ftp.quit()
        
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
