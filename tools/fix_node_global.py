
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def fix_node_path_globally():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. Find where 'node' actually is
    print("\n--- Searching for 'node' binary ---")
    # We look for 'bin/node' pattern to avoid npm modules or folders
    stdin, stdout, stderr = client.exec_command("find / -type f -name node 2>/dev/null | grep '/bin/node'")
    node_paths = stdout.read().decode().strip().split('\n')
    
    # Filter valid executables
    valid_node = None
    for path in node_paths:
        if not path: continue
        # Check if executable
        stdin, stdout, stderr = client.exec_command(f"test -x {path} && echo 'yes'")
        if 'yes' in stdout.read().decode():
            # Exclude node_modules (local installs)
            if 'node_modules' not in path:
                valid_node = path
                break
    
    if not valid_node:
        print("CRITICAL: Could not find any global node binary!")
        # Fallback check in common DFinans path user mentioned
        stdin, stdout, stderr = client.exec_command("ls /var/www/DigageFinans/runtime_node/bin/node")
        if not stderr.read():
            valid_node = "/var/www/DigageFinans/runtime_node/bin/node"
            
    if valid_node:
        print(f"Found Node at: {valid_node}")
        
        # 2. Check current system path for node
        print("\n--- Checking /usr/bin/node and /usr/local/bin/node ---")
        
        # Fix /usr/bin/node
        client.exec_command("rm -f /usr/bin/node") # Remove broken link if any
        client.exec_command(f"ln -s {valid_node} /usr/bin/node")
        print(f"Linked /usr/bin/node -> {valid_node}")

        # Fix /usr/local/bin/node (some scripts check here)
        client.exec_command("rm -f /usr/local/bin/node")
        client.exec_command(f"ln -s {valid_node} /usr/local/bin/node")
        print(f"Linked /usr/local/bin/node -> {valid_node}")
        
        # Fix npm as well?
        npm_path = valid_node.replace("node", "npm")
        # Verify npm exists there
        stdin, stdout, stderr = client.exec_command(f"ls {npm_path}")
        if not stderr.read():
             client.exec_command("rm -f /usr/bin/npm")
             client.exec_command(f"ln -s {npm_path} /usr/bin/npm")
             print(f"Linked /usr/bin/npm -> {npm_path}")

        # 3. Verify Fix
        print("\n--- Verifying 'node -v' ---")
        stdin, stdout, stderr = client.exec_command("node -v")
        print(f"Version: {stdout.read().decode().strip()}")
        
    else:
        print("Could not find a valid Node installation to link.")

    client.close()

if __name__ == '__main__':
    fix_node_path_globally()
