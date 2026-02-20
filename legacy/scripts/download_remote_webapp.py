import paramiko
import os
import sys

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_FILE = '/var/www/sustainage/web_app.py'
LOCAL_FILE = 'c:/SUSTAINAGESERVER/web_app_remote.py'

def download_remote_file():
    print(f"Downloading {REMOTE_FILE} from {HOSTNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
        sftp = ssh.open_sftp()
        sftp.get(REMOTE_FILE, LOCAL_FILE)
        sftp.close()
        ssh.close()
        print(f"File downloaded to {LOCAL_FILE}")
    except Exception as e:
        print(f"Failed to download: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_remote_file()
