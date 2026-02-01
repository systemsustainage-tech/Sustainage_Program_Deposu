import paramiko
import os
import sys
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b)"

LOCAL_FILE = "backend/core/language_manager.py"
REMOTE_FILE = "/var/www/sustainage/backend/core/language_manager.py"

def deploy_fix():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        print(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        print("Upload successful.")
        sftp.close()
        
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        
        # Wait for command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed. Error: {stderr.read().decode()}")
            
        ssh.close()
        
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    deploy_fix()
