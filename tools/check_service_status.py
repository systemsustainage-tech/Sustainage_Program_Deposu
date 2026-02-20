import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def check_status():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Use the same logic as restart_service.py
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        client.connect(HOST, username=USER, key_filename=key_filename)
        
        print(f"Connected to {HOST}. Checking service status...")
        
        # Check status
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        print("\n--- Service Status ---")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # Check recent logs
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print("\n--- Recent Logs ---")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        client.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_status()
