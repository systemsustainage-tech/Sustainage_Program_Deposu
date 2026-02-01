import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

REMOTE_PATH = "/var/www/sustainage/backend/modules/environmental/emission_factor_data.py"

def check_remote_file():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        try:
            attr = sftp.stat(REMOTE_PATH)
            print(f"File exists: {REMOTE_PATH}")
            print(f"Size: {attr.st_size} bytes")
            print(f"Mode: {oct(attr.st_mode)}")
        except FileNotFoundError:
            print(f"File NOT found: {REMOTE_PATH}")
            
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_remote_file()
