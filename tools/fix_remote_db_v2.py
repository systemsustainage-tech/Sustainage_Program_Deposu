import os
import subprocess
import time

# Configuration
REMOTE_HOST = "root@72.62.150.207"
REMOTE_DIR = "/var/www/sustainage"
LOCAL_DB = "backend/data/sdg_desktop.sqlite"
REMOTE_DB = f"{REMOTE_DIR}/backend/data/sdg_desktop.sqlite"

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Success: {result.stdout}")
    return True

def fix_database_v2():
    print("--- Fixing Remote Database V2 ---")
    
    # 0. Find systemctl
    print("Locating systemctl...")
    cmd_find = f"ssh {REMOTE_HOST} 'which systemctl'"
    result = subprocess.run(cmd_find, shell=True, capture_output=True, text=True)
    systemctl_path = "systemctl"
    if result.returncode == 0 and result.stdout.strip():
        systemctl_path = result.stdout.strip()
        print(f"Found systemctl at: {systemctl_path}")
    else:
        print("Could not find systemctl, trying default...")

    # 1. Stop service
    print("Stopping sustainage service...")
    if not run_command(f"ssh {REMOTE_HOST} '{systemctl_path} stop sustainage'"):
         print("Trying 'service' command instead...")
         run_command(f"ssh {REMOTE_HOST} 'service sustainage stop'")

    # 2. Upload healthy database
    print("Uploading healthy database...")
    cmd = f"scp {LOCAL_DB} {REMOTE_HOST}:{REMOTE_DB}"
    if not run_command(cmd):
        print("Failed to upload database.")
        # Don't return, try to restart anyway
    
    # 3. Fix permissions
    print("Fixing permissions...")
    run_command(f"ssh {REMOTE_HOST} 'chown -R www-data:www-data {REMOTE_DIR}/backend/data'")
    run_command(f"ssh {REMOTE_HOST} 'chmod 775 {REMOTE_DIR}/backend/data'")
    run_command(f"ssh {REMOTE_HOST} 'chmod 664 {REMOTE_DB}'")

    # 4. Restart service
    print("Restarting sustainage service...")
    if not run_command(f"ssh {REMOTE_HOST} '{systemctl_path} restart sustainage'"):
        print("Trying 'service' command...")
        run_command(f"ssh {REMOTE_HOST} 'service sustainage restart'")
    
    # 5. Check status
    print("Checking service status...")
    run_command(f"ssh {REMOTE_HOST} '{systemctl_path} status sustainage --no-pager'")

if __name__ == "__main__":
    fix_database_v2()
