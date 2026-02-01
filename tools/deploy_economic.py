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
        ('c:\\SUSTAINAGESERVER\\templates\\economic.html', '/var/www/sustainage/templates/economic.html'),
        ('c:\\SUSTAINAGESERVER\\templates\\benchmark.html', '/var/www/sustainage/templates/benchmark.html'),
        ('c:\\SUSTAINAGESERVER\\backend\\modules\\economic\\economic_manager.py', '/var/www/sustainage/backend/modules/economic/economic_manager.py'),
        ('c:\\SUSTAINAGESERVER\\backend\\modules\\economic\\__init__.py', '/var/www/sustainage/backend/modules/economic/__init__.py'),
        ('c:\\SUSTAINAGESERVER\\backend\\modules\\analytics\\sector_benchmark_database.py', '/var/www/sustainage/backend/modules/analytics/sector_benchmark_database.py'),
        ('c:\\SUSTAINAGESERVER\\web_app.py', '/var/www/sustainage/web_app.py')
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
                ssh.exec_command(f'mkdir -p {remote_dir}')
            
            sftp.put(local_path, remote_path)
        else:
            print(f"Warning: Local file not found: {local_path}")

    # Remove old file if exists
    try:
        sftp.remove('/var/www/sustainage/backend/modules/economic/economic_value_manager.py')
        print("Removed old economic_value_manager.py")
    except IOError:
        pass # File doesn't exist

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
