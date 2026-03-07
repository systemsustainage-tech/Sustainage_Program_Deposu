
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def find_and_start_pm2():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. Find PM2
    print("\n--- Searching for PM2 ---")
    stdin, stdout, stderr = client.exec_command("find / -name pm2 -type f 2>/dev/null")
    pm2_paths = stdout.read().decode().strip().split('\n')
    
    pm2_cmd = "pm2" # Default fallback
    for p in pm2_paths:
        if '/bin/pm2' in p:
            pm2_cmd = p
            break
            
    print(f"Using PM2 Command: {pm2_cmd}")

    # 2. Kill existing Node processes to clean slate
    print("\n--- Cleaning up existing Node processes ---")
    client.exec_command("pkill -f node")

    # 3. Start DigageFinans (Port 8003)
    print("\n--- Starting DigageFinans on Port 8003 ---")
    # Path based on ps aux: /root/DFinans/index.js
    # We explicitly set PORT env var
    cmd_df = f"cd /root/DFinans && PORT=8003 {pm2_cmd} start index.js --name digagefinans --force"
    stdin, stdout, stderr = client.exec_command(cmd_df)
    print(stdout.read().decode())
    print(stderr.read().decode())

    # 4. Find Transfer App (Port 8002)
    # We need to guess the path. Usually next to DFinans or in /var/www
    print("\n--- Searching for Transfer App ---")
    # Try common locations
    possible_paths = ["/var/www/transfer", "/root/transfer", "/var/www/Transfer", "/root/Transfer"]
    transfer_path = None
    
    # Simple check via ls
    for p in possible_paths:
        stdin, stdout, stderr = client.exec_command(f"ls {p}/package.json")
        if not stderr.read():
            transfer_path = p
            break
            
    if transfer_path:
        print(f"Found Transfer App at: {transfer_path}")
        print("\n--- Starting Transfer App on Port 8002 ---")
        # Check if it has a start script or index.js
        cmd_transfer = f"cd {transfer_path} && PORT=8002 {pm2_cmd} start npm --name transfer -- start --force" 
        # Or try index.js if exists
        stdin, stdout, stderr = client.exec_command(f"ls {transfer_path}/index.js")
        if not stderr.read():
             cmd_transfer = f"cd {transfer_path} && PORT=8002 {pm2_cmd} start index.js --name transfer --force"
             
        stdin, stdout, stderr = client.exec_command(cmd_transfer)
        print(stdout.read().decode())
    else:
        print("Could not locate Transfer App directory automatically. Please check manually.")

    # 5. Save and List
    print("\n--- Saving PM2 List ---")
    client.exec_command(f"{pm2_cmd} save")
    
    print("\n--- Final PM2 List ---")
    stdin, stdout, stderr = client.exec_command(f"{pm2_cmd} list")
    print(stdout.read().decode())

    client.close()

if __name__ == '__main__':
    find_and_start_pm2()
