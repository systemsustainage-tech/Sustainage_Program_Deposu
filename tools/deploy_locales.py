import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'
REMOTE_BASE_DIR = '/var/www/sustainage'
LOCAL_BASE_DIR = r'c:\SUSTAINAGESERVER'

def deploy_locales():
    print(f"Connecting to {HOSTNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()
        
        print("Deploying locales...")
        local_dir = os.path.join(LOCAL_BASE_DIR, 'locales')
        remote_dir = f"{REMOTE_BASE_DIR}/locales"
        
        for filename in os.listdir(local_dir):
            if filename.endswith('.json'):
                local_path = os.path.join(local_dir, filename)
                remote_path = f"{remote_dir}/{filename}"
                print(f"  Uploading {filename}...")
                sftp.put(local_path, remote_path)
        
        print("Done.")
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy_locales()
