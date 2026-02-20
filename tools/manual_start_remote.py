import paramiko
import os
import time

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_debug():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Check if key file exists
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=key_filename)
        
        print("\n--- Service Definition ---")
        stdin, stdout, stderr = ssh.exec_command("cat /etc/systemd/system/sustainage.service")
        print(stdout.read().decode())
        
        print("\n--- Manual Start Attempt (Dry Run) ---")
        # Try to import web_app and see if it crashes
        cmd = "cd /var/www/sustainage && ./venv/bin/python -c 'from web_app import app; print(\"Import Successful\")'"
        print(f"Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out: print(f"STDOUT: {out}")
        if err: print(f"STDERR: {err}")
        
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_debug()
