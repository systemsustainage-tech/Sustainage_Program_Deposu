import paramiko
import os
import sys

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILENAME = os.path.expanduser("~/.ssh/id_rsa")
if not os.path.exists(KEY_FILENAME):
    KEY_FILENAME = None

def run_check():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=KEY_FILENAME)
        
        sftp = ssh.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\tools\check_remote_dbs.py'
        remote_path = '/var/www/sustainage/tools/check_remote_dbs.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()
        
        print("Running check script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out:
            print("--- STDOUT ---")
            print(out)
        if err:
            print("--- STDERR ---")
            print(err)
            
        ssh.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_check()
