
import paramiko
import os
import time

HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"

LOCAL_SCRIPT = "c:\\SDG\\tools\\remote_schema_fix_columns.py"
REMOTE_SCRIPT = "/var/www/sustainage/tools/remote_schema_fix_columns.py"

def run_fix():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        sftp = ssh.open_sftp()
        
        # Ensure directory exists
        try:
            sftp.stat("/var/www/sustainage/tools")
        except FileNotFoundError:
            sftp.mkdir("/var/www/sustainage/tools")
            
        print(f"Uploading {LOCAL_SCRIPT} to {REMOTE_SCRIPT}...")
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()
        
        print("Running schema fix script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_SCRIPT}")
        
        exit_status = stdout.channel.recv_exit_status()
        print(stdout.read().decode())
        
        if exit_status != 0:
            print(f"Error: {stderr.read().decode()}")
        else:
            print("Schema fix executed successfully.")
            
        ssh.close()
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    run_fix()
