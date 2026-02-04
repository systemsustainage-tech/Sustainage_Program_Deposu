import os
import subprocess
import time

# Configuration
REMOTE_HOST = "root@72.62.150.207"
REMOTE_DIR = "/var/www/sustainage"
LOCAL_SCRIPT = "tools/verify_auth_direct.py"
REMOTE_SCRIPT = f"{REMOTE_DIR}/tools/verify_auth_direct.py"
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

def run_test():
    print("--- Running Remote Auth Test ---")
    
    # 1. Upload script
    print("Uploading script...")
    cmd = f"scp {LOCAL_SCRIPT} {REMOTE_HOST}:{REMOTE_SCRIPT}"
    if not run_command(cmd):
        print("Failed to upload script.")
        return

    # 2. Run script
    print("Executing script on remote...")
    run_command(f"ssh {REMOTE_HOST} 'python3 {REMOTE_SCRIPT}'", is_ssh=True)

if __name__ == "__main__":
    run_test()
