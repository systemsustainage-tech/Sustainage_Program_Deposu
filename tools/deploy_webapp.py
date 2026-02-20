import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def deploy_webapp():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)

        sftp = ssh.open_sftp()
        
        # Upload web_app.py
        local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web_app.py')
        remote_path = '/var/www/sustainage/web_app.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        print("Upload successful.")
        
        # Restart service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

        sftp.close()
        ssh.close()
        
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    deploy_webapp()
