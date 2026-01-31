import paramiko
import os
import sys

# Server Connection Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_FILE = r"c:\SDG\tools\create_missing_tables.py"
REMOTE_FILE = "/var/www/sustainage/tools/create_missing_tables.py"

def inspect():
    try:
        print(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        
        # Ensure tools dir exists
        try:
            sftp.mkdir("/var/www/sustainage/tools")
        except:
            pass

        print(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        
        sftp.close()
        
        print("Running inspection script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_FILE}")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Errors:\n{err}")
        
        ssh.close()
        print("Inspection complete.")
        
    except Exception as e:
        print(f"Inspection failed: {e}")

if __name__ == "__main__":
    inspect()
