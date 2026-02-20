import paramiko
import os
import sys

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILENAME = os.path.expanduser("~/.ssh/id_rsa")
if not os.path.exists(KEY_FILENAME):
    KEY_FILENAME = None

def deploy_config():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=KEY_FILENAME)
        
        sftp = ssh.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\backend\config\database.py'
        remote_path = '/var/www/sustainage/backend/config/database.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()
        
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy_config()
