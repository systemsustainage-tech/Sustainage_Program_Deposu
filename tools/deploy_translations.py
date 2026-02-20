import os
import paramiko
from datetime import datetime
import stat

# Configuration
REMOTE_HOST = "72.62.150.207"
REMOTE_USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_ed25519")
REMOTE_BASE = "/var/www/sustainage"

def create_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(REMOTE_HOST, username=REMOTE_USER, key_filename=KEY_FILE)
    return client

def ensure_remote_dir(sftp, remote_path):
    """Recursively ensure remote directory exists."""
    dirs = remote_path.split('/')
    path = ""
    for directory in dirs:
        if not directory: continue
        path += "/" + directory
        try:
            sftp.stat(path)
        except FileNotFoundError:
            try:
                sftp.mkdir(path)
                print(f"Created remote directory: {path}")
            except Exception as e:
                # Might fail if it's a file or permission issue
                print(f"Error creating {path}: {e}")

def upload_file(sftp, local_path, remote_path):
    try:
        # Ensure remote directory exists
        remote_dir = os.path.dirname(remote_path)
        ensure_remote_dir(sftp, remote_dir)
        
        sftp.put(local_path, remote_path)
        print(f"✅ Uploaded: {local_path} -> {remote_path}")
    except Exception as e:
        print(f"❌ Failed to upload {local_path}: {e}")

def upload_directory(sftp, local_dir, remote_dir):
    """Recursively upload a directory."""
    if not os.path.exists(local_dir):
        print(f"Skipping missing local directory: {local_dir}")
        return

    for root, dirs, files in os.walk(local_dir):
        # Calculate relative path to preserve structure
        rel_path = os.path.relpath(root, local_dir)
        if rel_path == ".":
            remote_current_dir = remote_dir
        else:
            remote_current_dir = f"{remote_dir}/{rel_path}".replace("\\", "/")
        
        for file in files:
            if file.endswith(".pyc") or file == "__pycache__": continue
            
            local_file_path = os.path.join(root, file)
            remote_file_path = f"{remote_current_dir}/{file}"
            upload_file(sftp, local_file_path, remote_file_path)

def deploy_translations():
    print(f"Starting deployment to {REMOTE_HOST}...")
    client = create_ssh_client()
    sftp = client.open_sftp()
    
    # 1. Deploy Root Locales
    upload_directory(sftp, r"c:\SUSTAINAGESERVER\locales", f"{REMOTE_BASE}/locales")

    # 2. Deploy Backend Locales
    upload_directory(sftp, r"c:\SUSTAINAGESERVER\backend\locales", f"{REMOTE_BASE}/backend/locales")

    # 3. Deploy remote_web_app.py
    upload_file(sftp, 
                r"c:\SUSTAINAGESERVER\remote_web_app.py", 
                f"{REMOTE_BASE}/remote_web_app.py")

    # 4. Deploy Templates
    upload_directory(sftp, r"c:\SUSTAINAGESERVER\templates", f"{REMOTE_BASE}/templates")

    # 5. Deploy Specific Backend Modules (Updates)
    # REST API Server (Hardcoded string fixes)
    upload_file(sftp,
                r"c:\SUSTAINAGESERVER\backend\modules\integration\rest_api_server.py",
                f"{REMOTE_BASE}/backend/modules/integration/rest_api_server.py")
    
    # Advanced Inventory
    upload_directory(sftp, 
                    r"c:\SUSTAINAGESERVER\backend\modules\advanced_inventory", 
                    f"{REMOTE_BASE}/backend/modules/advanced_inventory")

    # Advanced Calculation
    upload_directory(sftp, 
                    r"c:\SUSTAINAGESERVER\backend\modules\advanced_calculation", 
                    f"{REMOTE_BASE}/backend/modules/advanced_calculation")

    sftp.close()
    
    # 6. Restart Service
    print("Restarting sustainage.service...")
    stdin, stdout, stderr = client.exec_command("systemctl restart sustainage.service")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("✅ Service restarted successfully.")
    else:
        print(f"❌ Service restart failed: {stderr.read().decode()}")

    client.close()
    print("Deployment complete.")

if __name__ == "__main__":
    deploy_translations()
