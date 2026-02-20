import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
REMOTE_PATH = "/var/www/sustainage/locales"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def upload_locales():
    print(f"Uploading locales to {HOST}:{REMOTE_PATH}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Match deploy_to_remote.py logic
        key_path = KEY_FILE if os.path.exists(KEY_FILE) else None
        print(f"Connecting with key: {key_path}")
        
        ssh.connect(HOST, username=USER, key_filename=key_path)
        sftp = ssh.open_sftp()
        
        local_dir = os.path.join(os.getcwd(), 'locales')
        for filename in os.listdir(local_dir):
            if filename.endswith('.json'):
                local_file = os.path.join(local_dir, filename)
                remote_file = f"{REMOTE_PATH}/{filename}"
                print(f"Uploading {filename} ({os.path.getsize(local_file)} bytes)...")
                sftp.put(local_file, remote_file)
                
        print("Done.")
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    upload_locales()
