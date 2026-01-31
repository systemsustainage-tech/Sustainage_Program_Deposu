import paramiko
import os
import sys
import time

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_BASE = r'C:\SUSTAINAGESERVER'
REMOTE_BASE = '/var/www/sustainage'

def deploy_directory(sftp, local_dir, remote_dir):
    """Recursively deploys a directory to the remote server."""
    print(f"Deploying directory: {local_dir} -> {remote_dir}")
    
    # Create remote directory if it doesn't exist
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        try:
            sftp.mkdir(remote_dir)
            print(f"Created remote directory: {remote_dir}")
        except Exception as e:
            # Try creating parent first? or use mkdir -p via command
            print(f"Error creating directory {remote_dir}: {e}. Trying via command later or ignoring if parent exists.")

    for item in os.listdir(local_dir):
        if item == '__pycache__' or item.endswith('.pyc'):
            continue
            
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"
        
        if os.path.isdir(local_path):
            deploy_directory(sftp, local_path, remote_path)
        else:
            print(f"Uploading {item}...")
            sftp.put(local_path, remote_path)

def deploy():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        sftp = client.open_sftp()
        
        # Deploy backend/yonetim
        local_yonetim = os.path.join(LOCAL_BASE, 'backend', 'yonetim')
        remote_yonetim = f"{REMOTE_BASE}/backend/yonetim"
        
        # Ensure parent backend dir exists
        try:
            client.exec_command(f"mkdir -p {remote_yonetim}")
        except:
            pass

        deploy_directory(sftp, local_yonetim, remote_yonetim)

        # Set permissions
        print("Setting permissions...")
        client.exec_command(f"chown -R www-data:www-data {REMOTE_BASE}")
        client.exec_command(f"chmod -R 775 {REMOTE_BASE}")
        
        # Restart Service
        print("Restarting Service...")
        client.exec_command("systemctl restart sustainage")
        client.exec_command("pkill -HUP gunicorn")
        
        time.sleep(3)
        
        # Check status
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print("Service Status:\n", stdout.read().decode())

        sftp.close()
        client.close()
        print("Deployment of 'backend/yonetim' completed.")

    except Exception as e:
        print(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    deploy()
