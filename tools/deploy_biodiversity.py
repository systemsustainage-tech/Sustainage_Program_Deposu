import paramiko
import os
from datetime import datetime

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy():
    print(f"Connecting to {HOSTNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)

    sftp = ssh.open_sftp()

    files_to_deploy = [
        ('c:\\SUSTAINAGESERVER\\templates\\biodiversity.html', '/var/www/sustainage/templates/biodiversity.html'),
        ('c:\\SUSTAINAGESERVER\\backend\\modules\\environmental\\biodiversity_manager.py', '/var/www/sustainage/backend/modules/environmental/biodiversity_manager.py')
    ]

    for local_path, remote_path in files_to_deploy:
        if os.path.exists(local_path):
            print(f"Uploading {local_path} -> {remote_path}")
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path)
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                print(f"Creating remote directory: {remote_dir}")
                # This is a simple mkdir, for nested dirs it might fail if parent doesn't exist
                # But backend/modules/environmental likely exists
                ssh.exec_command(f'mkdir -p {remote_dir}')
            
            sftp.put(local_path, remote_path)
        else:
            print(f"Warning: Local file not found: {local_path}")

    sftp.close()

    print("Restarting service...")
    stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage.service')
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("Service restarted successfully.")
    else:
        print(f"Error restarting service: {stderr.read().decode()}")

    ssh.close()
    print("Deployment complete.")

if __name__ == "__main__":
    deploy()
