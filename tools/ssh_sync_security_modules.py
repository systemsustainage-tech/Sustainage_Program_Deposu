
import paramiko
import os
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
LOCAL_DIR = r'c:\SDG\server\backend\modules\security'
REMOTE_DIR = '/var/www/sustainage/backend/modules/security'

def sync_security():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        sftp = client.open_sftp()
        
        # Ensure remote dir exists
        client.exec_command(f'mkdir -p {REMOTE_DIR}')
        
        # List local files
        files = [f for f in os.listdir(LOCAL_DIR) if f.endswith('.py')]
        
        for f in files:
            local_path = os.path.join(LOCAL_DIR, f)
            remote_path = f"{REMOTE_DIR}/{f}"
            print(f"Uploading {f}...")
            sftp.put(local_path, remote_path)
            
        sftp.close()
        
        print("Restarting service...")
        client.exec_command("systemctl restart sustainage")
        time.sleep(3)
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    sync_security()
