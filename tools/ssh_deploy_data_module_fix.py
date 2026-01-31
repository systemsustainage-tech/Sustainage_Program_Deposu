import paramiko
import os
import sys

# Server Connection Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

FILES_TO_DEPLOY = [
    (r"c:\SDG\server\web_app.py", "/var/www/sustainage/web_app.py"),
    (r"c:\SDG\server\templates\data_edit.html", "/var/www/sustainage/templates/data_edit.html")
]

def deploy():
    try:
        print(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        
        for local, remote in FILES_TO_DEPLOY:
            print(f"Uploading {local} to {remote}...")
            sftp.put(local, remote)
        
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
