
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def final_check():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. Extensive Search for Transfer App
    print("\n--- Deep Search for Transfer App ---")
    # Search for directories containing 'transfer' case-insensitive
    stdin, stdout, stderr = client.exec_command("find /var/www /root -type d -iname '*transfer*' 2>/dev/null")
    candidates = stdout.read().decode().strip().split('\n')
    
    transfer_app_path = None
    for path in candidates:
        if not path: continue
        # Check if it has package.json or index.js
        stdin, stdout, stderr = client.exec_command(f"ls {path}/package.json {path}/index.js")
        if not stderr.read():
            transfer_app_path = path
            break
            
    if transfer_app_path:
        print(f"Found Transfer App Candidate: {transfer_app_path}")
        print("Starting Transfer App...")
        # Try start script first
        cmd = f"cd {transfer_app_path} && PORT=8002 pm2 start npm --name transfer -- start --force"
        # If no start script, fallback to index.js
        # But let's just try npm start as it is safer for React/Next apps
        client.exec_command(cmd)
    else:
        print("Still could not find Transfer App. It might be named differently or not deployed.")

    # 2. Check Sustainage Service
    print("\n--- Checking Sustainage Service ---")
    stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
    print(stdout.read().decode())
    
    # 3. Final PM2 List
    print("\n--- PM2 List ---")
    stdin, stdout, stderr = client.exec_command("pm2 list")
    print(stdout.read().decode())
    
    # Save
    client.exec_command("pm2 save")

    client.close()

if __name__ == '__main__':
    final_check()
