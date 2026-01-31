import paramiko
import os
import time

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES_TO_DEPLOY = [
    {'local': 'backend/yonetim/kullanici_yonetimi/models/user_manager.py', 'remote': '/var/www/sustainage/backend/yonetim/kullanici_yonetimi/models/user_manager.py'},
    {'local': 'web_app.py', 'remote': '/var/www/sustainage/web_app.py'},
    {'local': 'tools/fix_users.py', 'remote': '/var/www/sustainage/tools/fix_users.py'},
]

def deploy():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")

        sftp = client.open_sftp()

        for file_info in FILES_TO_DEPLOY:
            local_path = os.path.join(BASE_DIR, file_info['local'])
            remote_path = file_info['remote']
            
            if not os.path.exists(local_path):
                print(f"Skipping missing local file: {local_path}")
                continue

            print(f"Uploading {local_path} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
                print("Uploaded.")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")

        sftp.close()

        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command('systemctl restart sustainage')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

        client.close()

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
