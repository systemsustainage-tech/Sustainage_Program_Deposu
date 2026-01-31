
import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"

LOCAL_PATH = "c:\\SDG\\server\\templates\\base.html"
REMOTE_PATH = "/var/www/sustainage/templates/base.html"

def deploy_base():
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
        ssh.exec_command("systemctl restart sustainage")
        
        ssh.close()
        print("Done.")
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy_base()
