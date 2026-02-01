import paramiko
import os
import sys
import glob
from scp import SCPClient

# Remote server details
HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"
REMOTE_PATH = "/var/www/sustainage"

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

def deploy_locales():
    client = create_ssh_client()
    
    # Local locales path
    local_locales_dir = os.path.join(os.getcwd(), "backend", "locales")
    if not os.path.exists(local_locales_dir):
        print(f"Local locales directory not found: {local_locales_dir}")
        return

    # Find all JSON files
    json_files = glob.glob(os.path.join(local_locales_dir, "*.json"))
    
    files_to_deploy = []
    for f in json_files:
        rel_path = os.path.relpath(f, os.getcwd())
        files_to_deploy.append((f, rel_path.replace("\\", "/"))) # Ensure forward slashes for remote
    
    # Also include core/language_manager.py
    core_lang_mgr = os.path.join(os.getcwd(), "backend", "core", "language_manager.py")
    if os.path.exists(core_lang_mgr):
        files_to_deploy.append((core_lang_mgr, "backend/core/language_manager.py"))

    try:
        with SCPClient(client.get_transport()) as scp:
            for local_path, remote_rel_path in files_to_deploy:
                remote_full_path = f"{REMOTE_PATH}/{remote_rel_path}"
                
                print(f"Uploading {os.path.basename(local_path)} to {remote_full_path}...")
                
                # Ensure remote directory exists
                remote_dir = os.path.dirname(remote_full_path)
                stdin, stdout, stderr = client.exec_command(f"mkdir -p {remote_dir}")
                stdout.channel.recv_exit_status()
                
                scp.put(local_path, remote_full_path)
                
        print(f"Deployed {len(files_to_deploy)} files successfully.")
        
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
    deploy_locales()
