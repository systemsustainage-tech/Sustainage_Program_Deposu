import os
import subprocess
import time

# Configuration
REMOTE_HOST = "root@72.62.150.207"
REMOTE_DIR = "/var/www/sustainage"
LOCAL_FILE = "backend/yonetim/security/core/crypto.py"
REMOTE_FILE = f"{REMOTE_DIR}/backend/yonetim/security/core/crypto.py"
PATH_EXPORT = "export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin;"

def run_command(command, is_ssh=False):
    full_cmd = command
    if is_ssh:
        raw_cmd = command.replace(f"ssh {REMOTE_HOST} ", "").strip()
        if raw_cmd.startswith("'") and raw_cmd.endswith("'"):
            raw_cmd = raw_cmd[1:-1]
        elif raw_cmd.startswith('"') and raw_cmd.endswith('"'):
            raw_cmd = raw_cmd[1:-1]
            
        full_cmd = f'ssh {REMOTE_HOST} "{PATH_EXPORT} {raw_cmd}"'
    
    print(f"Running: {full_cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def deploy_crypto():
    print("--- Deploying crypto.py ---")
    
    # 1. Upload file
    print("Uploading crypto.py...")
    cmd = f"scp {LOCAL_FILE} {REMOTE_HOST}:{REMOTE_FILE}"
    if not run_command(cmd):
        print("Failed to upload crypto.py.")
        return

    # 2. Restart service
    print("Restarting sustainage service...")
    if not run_command(f"ssh {REMOTE_HOST} 'systemctl restart sustainage'", is_ssh=True):
        print("Trying 'service' command...")
        run_command(f"ssh {REMOTE_HOST} 'service sustainage restart'", is_ssh=True)
    
    # 3. Check status
    print("Checking service status...")
    run_command(f"ssh {REMOTE_HOST} 'systemctl status sustainage --no-pager'", is_ssh=True)

if __name__ == "__main__":
    deploy_crypto()
