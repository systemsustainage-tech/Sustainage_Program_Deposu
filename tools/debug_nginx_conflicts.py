
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def fix_nginx():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. List active sites to identify duplicates
    print("\n--- Checking Enabled Sites ---")
    cmd_list = "ls -l /etc/nginx/sites-enabled/"
    stdin, stdout, stderr = client.exec_command(cmd_list)
    print(stdout.read().decode())

    # 2. Check content of digagefinans configs
    print("\n--- Checking digagefinans Configs ---")
    # We suspect multiple files might define 'digagefinans.com'
    cmd_grep = "grep -l 'server_name.*digagefinans.com' /etc/nginx/sites-enabled/*"
    stdin, stdout, stderr = client.exec_command(cmd_grep)
    files = stdout.read().decode().strip().split('\n')
    
    print(f"Files defining digagefinans.com: {files}")
    
    if len(files) > 1:
        print("\n!!! DUPLICATE CONFIGS DETECTED !!!")
        print("Safely disabling duplicates (keeping the one that looks most recent or standard)...")
        
        # Strategy: Keep 'digagefinans.com' or 'digagefinans', disable others by removing symlink
        # We will just print them for now to be safe, as requested by user
        for f in files:
            print(f"\n--- Content of {f} ---")
            stdin, stdout, stderr = client.exec_command(f"cat {f}")
            print(stdout.read().decode())
            
    else:
        print("No duplicates found for digagefinans.com via grep. Checking other potential conflicts...")
        
    client.close()

if __name__ == '__main__':
    fix_nginx()
