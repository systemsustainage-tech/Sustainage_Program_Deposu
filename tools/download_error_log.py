import os
import paramiko
from datetime import datetime

# FTP/SFTP Configuration
FTP_HOST = "72.62.150.207"
FTP_USER = "sustaina"
FTP_PASS = "Sustain_2024!"
REMOTE_LOG_PATH = "/logs/error_log"  # Common location, might need adjustment
LOCAL_LOG_PATH = "c:/SDG/temp_diagnose/server_error.log"

def download_error_log():
    try:
        transport = paramiko.Transport((FTP_HOST, 22))
        transport.connect(username=FTP_USER, password=FTP_PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Try to find the error log. Locations vary by hosting.
        # Common plesk/cpanel locations:
        # /logs/error_log
        # /statistics/logs/error_log
        # /var/www/vhosts/sustainage.cloud/logs/error_log
        
        possible_paths = [
            "/logs/error_log",
            "/statistics/logs/error_log",
            "logs/error_log",
            "error_log"
        ]
        
        remote_path = None
        for path in possible_paths:
            try:
                sftp.stat(path)
                remote_path = path
                print(f"Found error log at: {path}")
                break
            except FileNotFoundError:
                continue
        
        if remote_path:
            os.makedirs(os.path.dirname(LOCAL_LOG_PATH), exist_ok=True)
            sftp.get(remote_path, LOCAL_LOG_PATH)
            print(f"Downloaded error log to {LOCAL_LOG_PATH}")
            
            # Read last 100 lines
            with open(LOCAL_LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                print("\n--- Last 100 lines of Error Log ---")
                for line in lines[-100:]:
                    print(line.strip())
        else:
            print("Could not find error_log in common locations.")
            print("Listing root directory:")
            print(sftp.listdir('.'))
            try:
                print("Listing /logs directory:")
                print(sftp.listdir('/logs'))
            except:
                pass

        sftp.close()
        transport.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    download_error_log()
