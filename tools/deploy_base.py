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

    local_file = 'c:\\SUSTAINAGESERVER\\templates\\base.html'
    remote_file = '/var/www/sustainage/templates/base.html'

    print(f"Uploading {local_file} -> {remote_file}")
    sftp.put(local_file, remote_file)
    
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
