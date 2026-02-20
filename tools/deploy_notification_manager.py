import paramiko
import os
import time

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
LOCAL_FILE = r'c:\SUSTAINAGESERVER\backend\modules\notification\notification_manager.py'
REMOTE_PATH = '/var/www/sustainage/backend/modules/notification/notification_manager.py'

def upload_file():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=KEY_FILE)
        
        sftp = ssh.open_sftp()
        print(f"Uploading {LOCAL_FILE} to {REMOTE_PATH}...")
        sftp.put(LOCAL_FILE, REMOTE_PATH)
        print("Upload successful.")
        
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    upload_file()
