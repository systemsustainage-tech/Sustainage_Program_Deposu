import paramiko
import sys
import os

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

FILES_TO_UPLOAD = [
    ('c:/SUSTAINAGESERVER/locales/tr.json', '/var/www/sustainage/locales/tr.json'),
    ('c:/SUSTAINAGESERVER/backend/locales/tr.json', '/var/www/sustainage/backend/locales/tr.json')
]

def upload_file(local_path, remote_path):
    print(f"Uploading {local_path} to {remote_path}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
        sftp = ssh.open_sftp()
        try:
            sftp.put(local_path, remote_path)
            print(f"Uploaded {remote_path}")
        except Exception as e:
            print(f"Failed to upload {remote_path}: {e}")
        sftp.close()
        
        # Restart service
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")
            
        ssh.close()
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    for local, remote in FILES_TO_UPLOAD:
        upload_file(local, remote)
