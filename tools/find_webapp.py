
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
        
        target_file = 'web_app.py'
        found_files = []

        def traverse(path):
            try:
                ftp.cwd(path)
                items = []
                ftp.dir(items.append)
                
                for item in items:
                    parts = item.split()
                    name = parts[-1]
                    if name in ['.', '..']: continue
                    
                    full_path = f"{path}/{name}" if path != '/' else f"/{name}"
                    
                    if item.startswith('d'):
                        # Directory
                        # Skip some heavy dirs to be fast
                        if name not in ['node_modules', 'venv', '.git', '__pycache__']:
                             traverse(full_path)
                    else:
                        # File
                        if name == target_file:
                            logging.info(f"FOUND: {full_path} - {item}")
                            found_files.append(full_path)
                            
                ftp.cwd('..')
            except Exception as e:
                # logging.warning(f"Error accessing {path}: {e}")
                pass

        logging.info("Searching for web_app.py recursively...")
        traverse('/')
        
        logging.info(f"Search complete. Found {len(found_files)} instances.")
        
        ftp.quit()
        
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
