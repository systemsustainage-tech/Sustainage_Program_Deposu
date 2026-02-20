import paramiko
import os
import sys

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def get_remote_logs():
    print(f"Connecting to {HOSTNAME} to fetch logs...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Check if key file exists
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=key_filename)
        
        print("\n--- Service Status ---")
        stdin, stdout, stderr = ssh.exec_command("systemctl status sustainage -l --no-pager")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\n--- Recent Service Logs (Journalctl) ---")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\n--- Nginx Error Logs ---")
        stdin, stdout, stderr = ssh.exec_command("tail -n 20 /var/log/nginx/error.log")
        print(stdout.read().decode())
        print(stderr.read().decode())

        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    get_remote_logs()
