import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_verification():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)

        sftp = ssh.open_sftp()
        
        # Upload verify_remote_schema.py
        local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools', 'verify_remote_schema.py')
        remote_path = '/var/www/sustainage/tools/verify_remote_schema.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        try:
            sftp.stat('/var/www/sustainage/tools')
        except IOError:
            sftp.mkdir('/var/www/sustainage/tools')
            
        sftp.put(local_path, remote_path)
        
        # Run the script
        print("Running verification script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        ssh.close()
        
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    run_verification()
