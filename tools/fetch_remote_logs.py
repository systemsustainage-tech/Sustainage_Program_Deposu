import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def fetch_logs():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {HOST}...")
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        # Execute
        print("Fetching logs...")
        cmd = "journalctl -u sustainage.service -n 100 --no-pager"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        logs = stdout.read().decode()
        print("--- LOGS ---")
        print(logs)
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_logs()
