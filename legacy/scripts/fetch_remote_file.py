import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def fetch_file(remote_path, local_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        sftp = client.open_sftp()
        print(f"Downloading {remote_path} to {local_path}...")
        sftp.get(remote_path, local_path)
        print("Download complete.")
        sftp.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fetch_file('/var/www/sustainage/backend/yonetim/security/core/crypto.py', 'c:\\SUSTAINAGESERVER\\remote_crypto.py')