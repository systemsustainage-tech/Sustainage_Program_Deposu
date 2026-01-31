import ftplib
import os
import sys

FTP_HOST = '72.62.150.207'
FTP_USER = 'cursorsustainageftp'
FTP_PASS = 'Kayra_1507_Sk!'
REMOTE_DB_PATH = '/httpdocs/backend/data/sdg_desktop.sqlite'
LOCAL_DB_PATH = 'c:/SDG/server/backend/data/sdg_desktop.sqlite'

def main():
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"Local DB not found at {LOCAL_DB_PATH}")
        return

    print(f"Connecting to FTP {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")
        
        # Backup remote DB just in case (rename it)
        try:
            ftp.rename(REMOTE_DB_PATH, REMOTE_DB_PATH + '.bak_empty')
            print("Renamed existing remote DB to .bak_empty")
        except:
            print("No existing remote DB to backup or rename failed (maybe didn't exist).")

        print(f"Uploading {LOCAL_DB_PATH}...")
        with open(LOCAL_DB_PATH, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_DB_PATH}', f)
        print("Upload complete.")
        
        # Restart app by touching web_app.py
        print("Restarting app...")
        try:
             # Download web_app.py to temp
             with open('temp_web_app.py', 'wb') as f:
                 ftp.retrbinary('RETR /httpdocs/web_app.py', f.write)
             # Upload it back
             with open('temp_web_app.py', 'rb') as f:
                 ftp.storbinary('STOR /httpdocs/web_app.py', f)
             os.remove('temp_web_app.py')
             print("App restarted (touched web_app.py).")
        except Exception as e:
            print(f"Failed to restart app: {e}")

        ftp.quit()
        
    except Exception as e:
        print(f"FTP Error: {e}")

if __name__ == '__main__':
    main()
