
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_investigation():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    commands = [
        "pm2 list",  # Check PM2 processes
        "pm2 resurrect", # Try to bring back saved processes
        "netstat -tuln | grep LISTEN", # Check open ports
        "ps aux | grep node", # Check running node processes
        "systemctl status nginx --no-pager", # Check main reverse proxy
        "cat /etc/nginx/sites-enabled/* | grep server_name" # List configured domains
    ]
    
    for cmd in commands:
        print(f"\n--- Running: {cmd} ---")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        if out:
            print(out)
        if err and "command not found" not in err:
            print(f"STDERR: {err}")

    client.close()

if __name__ == '__main__':
    run_investigation()
