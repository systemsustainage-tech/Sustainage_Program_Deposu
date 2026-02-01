import paramiko
import os
from scp import SCPClient

# Server connection details
HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = "Sustainage123!"
REMOTE_DIR = "/var/www/sustainage"

# Files to deploy (Local Path, Remote Relative Path)
FILES_TO_DEPLOY = [
    ("backend/modules/social/training_manager.py", "backend/modules/social/training_manager.py"),
    ("backend/modules/surveys/hosting_survey_manager.py", "backend/modules/surveys/hosting_survey_manager.py"),
    ("templates/training.html", "templates/training.html"),
    ("templates/survey_detail.html", "templates/survey_detail.html"),
    ("web_app.py", "web_app.py"),
    ("PLANNED_IMPROVEMENTS.md", "PLANNED_IMPROVEMENTS.md")
]

def deploy_files():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # SCP Client
        scp = SCPClient(ssh.get_transport())
        print("Connected. Uploading files...")

        for local_path, remote_rel_path in FILES_TO_DEPLOY:
            remote_path = f"{REMOTE_DIR}/{remote_rel_path}"
            
            # Ensure local file exists
            if not os.path.exists(local_path):
                print(f"Error: Local file not found: {local_path}")
                continue

            try:
                print(f"Uploading {local_path} -> {remote_path}")
                scp.put(local_path, remote_path)
            except Exception as e:
                print(f"Error uploading {local_path}: {e}")

        scp.close()
        
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

        ssh.close()
        print("Deployment completed successfully.")

    except Exception as e:
        print(f"Connection/Deployment failed: {e}")

if __name__ == "__main__":
    deploy_files()
