import os
import paramiko
import time

# Remote Server Configuration
HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = os.environ.get("REMOTE_SSH_PASS", "Kayra_1507")  # Fallback if env var not set

# Files to upload
FILES_TO_UPLOAD = [
    {'local': 'backend/modules/social/social_manager.py', 'remote': '/var/www/sustainage/backend/modules/social/social_manager.py'},
    {'local': 'web_app.py', 'remote': '/var/www/sustainage/web_app.py'},
    {'local': 'templates/social.html', 'remote': '/var/www/sustainage/templates/social.html'}
]

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        
        for item in FILES_TO_UPLOAD:
            local_path = item['local']
            remote_path = item['remote']
            if os.path.exists(local_path):
                print(f"Uploading {local_path} to {remote_path}...")
                try:
                    sftp.put(local_path, remote_path)
                except Exception as e:
                    print(f"Error uploading {local_path}: {e}")
            else:
                print(f"Local file not found: {local_path}")
        
        sftp.close()
        
        print("Restarting services...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service 'sustainage' restarted successfully.")
        else:
            print("Error restarting service 'sustainage':")
            print(stderr.read().decode())
        
        # Check status
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Deployment error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
