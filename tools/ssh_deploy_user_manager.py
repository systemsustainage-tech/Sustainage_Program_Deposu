import paramiko
import os
import sys

# Server Connection Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_FILE = r"c:\SDG\yonetim\kullanici_yonetimi\models\user_manager.py"
REMOTE_FILE = "/var/www/sustainage/yonetim/kullanici_yonetimi/models/user_manager.py"

def deploy():
    try:
        print(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        
        print(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        
        sftp.close()
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
        print("Deployment complete.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
