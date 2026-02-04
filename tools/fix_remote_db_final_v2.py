import os
import subprocess
import time

# Configuration
REMOTE_HOST = "root@72.62.150.207"
REMOTE_DIR = "/var/www/sustainage"
LOCAL_DB = "backend/data/sdg_desktop.sqlite"
REMOTE_DB = f"{REMOTE_DIR}/backend/data/sdg_desktop.sqlite"
PATH_EXPORT = "export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin;"

def run_command(command, is_ssh=False):
    full_cmd = command
    if is_ssh:
        # Inject PATH into the ssh command
        # command is like: ssh root@IP 'cmd'
        # we want: ssh root@IP "export PATH=...; cmd"
        
        # Strip existing quotes if any
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

def fix_database_final_v2():
    print("--- Fixing Remote Database Final V2 ---")
    
    # 1. Stop service
    print("Stopping sustainage service...")
    if not run_command(f"ssh {REMOTE_HOST} 'systemctl stop sustainage'", is_ssh=True):
         print("Trying 'service' command instead...")
         run_command(f"ssh {REMOTE_HOST} 'service sustainage stop'", is_ssh=True)

    # 2. Upload healthy database
    print("Uploading healthy database...")
    cmd = f"scp {LOCAL_DB} {REMOTE_HOST}:{REMOTE_DB}"
    if not run_command(cmd):
        print("Failed to upload database.")
        # proceed anyway
    
    # 3. Fix permissions
    print("Fixing permissions...")
    run_command(f"ssh {REMOTE_HOST} 'chown -R www-data:www-data {REMOTE_DIR}/backend/data'", is_ssh=True)
    run_command(f"ssh {REMOTE_HOST} 'chmod 775 {REMOTE_DIR}/backend/data'", is_ssh=True)
    run_command(f"ssh {REMOTE_HOST} 'chmod 664 {REMOTE_DB}'", is_ssh=True)

    # 4. Restart service
    print("Restarting sustainage service...")
    if not run_command(f"ssh {REMOTE_HOST} 'systemctl restart sustainage'", is_ssh=True):
        print("Trying 'service' command...")
        run_command(f"ssh {REMOTE_HOST} 'service sustainage restart'", is_ssh=True)
    
    # 5. Check status
    print("Checking service status...")
    run_command(f"ssh {REMOTE_HOST} 'systemctl status sustainage --no-pager'", is_ssh=True)

if __name__ == "__main__":
    fix_database_final_v2()
