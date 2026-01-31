import paramiko
import os
import sys

# Server Details
HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"
REMOTE_PATH = "/var/www/sustainage/web_app.py"
LOCAL_PATH = "c:\\SDG\\server\\web_app.py"

def deploy_fix():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        sftp = ssh.open_sftp()
        print(f"Uploading {LOCAL_PATH} to {REMOTE_PATH}...")
        sftp.put(LOCAL_PATH, REMOTE_PATH)
        sftp.close()
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        ssh.close()
        return True
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    if deploy_fix():
        print("Fix deployed successfully.")
    else:
        sys.exit(1)
