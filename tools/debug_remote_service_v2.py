import paramiko
import os
import time

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_command(ssh, command, title):
    print(f"\n--- {title} ---")
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        # Wait for command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        if out:
            print(out)
        if err:
            print(f"STDERR: {err}")
            
    except Exception as e:
        print(f"Error running command '{command}': {e}")

def get_remote_logs():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Check if key file exists
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        if not key_filename:
             print("Key file not found, trying default agent...")
        
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=key_filename)
        
        run_command(ssh, "systemctl status sustainage -l --no-pager", "Service Status")
        run_command(ssh, "journalctl -u sustainage -n 100 --no-pager", "Service Logs")
        run_command(ssh, "tail -n 20 /var/log/nginx/error.log", "Nginx Error Log")
        
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    get_remote_logs()
