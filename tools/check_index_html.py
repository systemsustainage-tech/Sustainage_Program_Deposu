
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
        
        logging.info("Downloading index.html...")
        with open('downloaded_index.html', 'wb') as f:
            ftp.retrbinary('RETR /httpdocs/index.html', f.write)
            
        with open('downloaded_index.html', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            print("--- index.html Content Start ---")
            print(content[:500])
            print("...")
            if "UserManager kullanilamiyor" in content:
                logging.info("FOUND 'UserManager kullanilamiyor' in index.html! This is a static file masking the app.")
            else:
                logging.info("String NOT found in index.html")
            print("--- index.html Content End ---")
            
        ftp.quit()
        
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
