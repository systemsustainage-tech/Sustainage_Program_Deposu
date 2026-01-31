import paramiko
import os
import time

# Remote server configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = os.environ.get('REMOTE_SSH_PASS', 'Kayra_1507')  # Fallback to known password if env var not set

def deploy_changes():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = client.open_sftp()
        
        # 1. Deploy social_manager.py
        local_path = 'backend/modules/social/social_manager.py'
        remote_path = '/var/www/sustainage/backend/modules/social/social_manager.py'
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        # 2. Deploy web_app.py
        local_path = 'web_app.py'
        remote_path = '/var/www/sustainage/web_app.py'
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        # 3. Deploy social.html
        local_path = 'templates/social.html'
        remote_path = '/var/www/sustainage/templates/social.html'
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        sftp.close()
        
        # 4. Restart Service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        # 5. Check status
        print("Checking service status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Deployment error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_changes()
