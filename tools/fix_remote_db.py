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

def fix_database():
    print("--- Fixing Remote Database ---")
    
    # 1. Stop service to release file lock
    print("Stopping sustainage service...")
    if not run_command(f"ssh {REMOTE_HOST} 'systemctl stop sustainage'"):
        print("Failed to stop service, proceeding anyway...")

    # 2. Upload healthy database
    print("Uploading healthy database...")
    # scp uses forward slashes even on windows for local path if run from git bash/powershell usually, but let's be safe
    # In python subprocess on windows, standard paths work.
    cmd = f"scp {LOCAL_DB} {REMOTE_HOST}:{REMOTE_DB}"
    if not run_command(cmd):
        print("Failed to upload database.")
        return

    # 3. Fix permissions
    print("Fixing permissions...")
    run_command(f"ssh {REMOTE_HOST} 'chown -R www-data:www-data {REMOTE_DIR}/backend/data'")
    run_command(f"ssh {REMOTE_HOST} 'chmod 775 {REMOTE_DIR}/backend/data'")
    run_command(f"ssh {REMOTE_HOST} 'chmod 664 {REMOTE_DB}'")

    # 4. Restart service
    print("Restarting sustainage service...")
    run_command(f"ssh {REMOTE_HOST} 'systemctl start sustainage'")
    
    # 5. Check status
    print("Checking service status...")
    run_command(f"ssh {REMOTE_HOST} 'systemctl status sustainage --no-pager'")

if __name__ == "__main__":
    fix_database()
