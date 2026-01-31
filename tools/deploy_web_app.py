import paramiko
import sys
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy_web_app():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    local_path = 'c:/SUSTAINAGESERVER/web_app.py'
    remote_path = '/var/www/sustainage/web_app.py'
    
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()
        
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage.service")
        
        # Wait for restart
        time.sleep(2)
        
        print("Checking service status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage.service")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Operation failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_web_app()
