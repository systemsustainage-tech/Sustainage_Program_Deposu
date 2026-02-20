import paramiko
import sys
import os

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

FILES = [
    '/var/www/sustainage/locales/tr.json',
    '/var/www/sustainage/backend/locales/tr.json'
]

def download_file(remote_path):
    local_path = os.path.basename(os.path.dirname(remote_path)) + '_' + os.path.basename(remote_path)
    # e.g. locales_tr.json or backend_locales_tr.json -> simpler: use suffix
    if 'backend' in remote_path:
        local_path = 'remote_backend_tr.json'
    else:
        local_path = 'remote_root_tr.json'
        
    print(f"Downloading {remote_path} to {local_path}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
        sftp = ssh.open_sftp()
        try:
            sftp.get(remote_path, local_path)
            print(f"Downloaded {local_path}")
        except Exception as e:
            print(f"Failed to download {remote_path}: {e}")
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    for f in FILES:
        download_file(f)
