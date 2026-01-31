
import os
import sys
from ftplib import FTP

# FTP Bilgileri
FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
REMOTE_DIR = '/httpdocs'

def deploy_file(local_path, remote_path):
    print(f"Uploading {local_path} to {remote_path}...")
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_path}', f)
            
        # Dosya zaman damgasını güncellemek için (uygulamanın yeniden başlamasını tetikleyebilir)
        try:
            ftp.voidcmd(f'MDTM {remote_path}')
        except:
            pass
            
        ftp.quit()
        print("Upload successful!")
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

if __name__ == "__main__":
    # web_app.py yükle
    local_file = "c:/SDG/server/web_app.py"
    remote_file = "/httpdocs/web_app.py"
    
    if os.path.exists(local_file):
        deploy_file(local_file, remote_file)
    else:
        print(f"File not found: {local_file}")
