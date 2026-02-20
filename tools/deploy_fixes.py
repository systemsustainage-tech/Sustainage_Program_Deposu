import paramiko
import os
import sys

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

FILES_TO_DEPLOY = [
    {
        'local': r'c:\SUSTAINAGESERVER\backend\modules\notification\notification_manager.py',
        'remote': '/var/www/sustainage/backend/modules/notification/notification_manager.py'
    },
    {
        'local': r'c:\SUSTAINAGESERVER\backend\modules\file_manager\advanced_file_manager.py',
        'remote': '/var/www/sustainage/backend/modules/file_manager/advanced_file_manager.py'
    }
]

def deploy_files():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Check if key file exists
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        if not key_filename:
            print(f"Warning: SSH key file {KEY_FILE} not found. Trying default authentication.")
            
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=key_filename)
        sftp = ssh.open_sftp()
        
        for item in FILES_TO_DEPLOY:
            local_path = item['local']
            remote_path = item['remote']
            print(f"Uploading {local_path} -> {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
                print("Success.")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
        
        sftp.close()
        
        # Restart service
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
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    deploy_files()
