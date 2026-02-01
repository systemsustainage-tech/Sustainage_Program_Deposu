import paramiko
import os
import sys
from scp import SCPClient

# Remote server details
HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"  # Password authentication
REMOTE_PATH = "/var/www/sustainage"

# Files to deploy
FILES_TO_DEPLOY = [
    ("backend/modules/training/training_manager.py", "backend/modules/training/training_manager.py"),
    ("backend/modules/stakeholder/stakeholder_engagement.py", "backend/modules/stakeholder/stakeholder_engagement.py"),
    ("templates/training.html", "templates/training.html"),
    ("web_app.py", "web_app.py"),
    ("PLANNED_IMPROVEMENTS.md", "PLANNED_IMPROVEMENTS.md")
]

def create_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        return client
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

def deploy_files():
    client = create_ssh_client()
    
    try:
        with SCPClient(client.get_transport()) as scp:
            for local_path, remote_rel_path in FILES_TO_DEPLOY:
                # Local path needs to be absolute or relative to CWD
                # We assume the script is run from project root or tools dir
                # Adjust local path if needed
                if not os.path.exists(local_path):
                     # Try checking relative to project root if we are in tools
                     if os.path.exists(os.path.join("..", local_path)):
                         local_path = os.path.join("..", local_path)
                     elif os.path.exists(os.path.join("c:\\SUSTAINAGESERVER", local_path)):
                         local_path = os.path.join("c:\\SUSTAINAGESERVER", local_path)
                
                remote_full_path = f"{REMOTE_PATH}/{remote_rel_path}"
                
                if not os.path.exists(local_path):
                    print(f"Skipping missing file: {local_path}")
                    continue
                
                print(f"Uploading {local_path} to {remote_full_path}...")
                
                # Ensure remote directory exists
                remote_dir = os.path.dirname(remote_full_path)
                stdin, stdout, stderr = client.exec_command(f"mkdir -p {remote_dir}")
                stdout.channel.recv_exit_status()
                
                scp.put(local_path, remote_full_path)
                
        print("Files deployed successfully.")
        
        # Restart Service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_files()
