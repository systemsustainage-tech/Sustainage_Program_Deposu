import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"
REMOTE_PATH = "/var/www/sustainage/backend/locales"

def check_locales():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        try:
            files = sftp.listdir(REMOTE_PATH)
            print(f"Files in {REMOTE_PATH}:")
            for f in files:
                # Check attributes
                attr = sftp.stat(f"{REMOTE_PATH}/{f}")
                print(f" - {f}")
                print(f"   Size: {attr.st_size} bytes")
                print(f"   Mode: {oct(attr.st_mode)}")
                print(f"   UID/GID: {attr.st_uid}/{attr.st_gid}")
                
        except FileNotFoundError:
            print(f"Directory {REMOTE_PATH} does not exist!")
            
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_locales()
