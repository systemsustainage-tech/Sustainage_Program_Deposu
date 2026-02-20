
import paramiko
import os
import time

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = r"C:\Users\Administrator\.ssh\id_rsa"
LOCAL_FILE = r"c:\SUSTAINAGESERVER\tools\create_remote_admin.py"
REMOTE_FILE = "/var/www/sustainage/tools/create_remote_admin.py"

def run_diagnostic():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    key_path = KEY_FILE if os.path.exists(KEY_FILE) else None
    print(f"Connecting with key: {key_path}")
    
    try:
        ssh.connect(HOST, username=USER, key_filename=key_path)
        sftp = ssh.open_sftp()
        
        print(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        sftp.close()
        
        print("Running script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_FILE}")
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print("Output:")
        print(output)
        
        if error:
            print("Error:")
            print(error)
            
        ssh.close()
    except Exception as e:
        print(f"SSH Error: {e}")

if __name__ == "__main__":
    run_diagnostic()
