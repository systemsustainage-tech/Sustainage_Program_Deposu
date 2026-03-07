
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def install_node_globally():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Current "bad" location
    current_node = "/var/www/DigageFinans/runtime_node"
    
    # 1. Create a proper directory in /opt
    print("\n--- Moving Node.js to /opt/node-v20 ---")
    target_dir = "/opt/node-v20"
    
    # Check if target already exists
    stdin, stdout, stderr = client.exec_command(f"test -d {target_dir} && echo 'exists'")
    if 'exists' in stdout.read().decode():
        print(f"Target {target_dir} already exists. Using it.")
    else:
        # Copy from the existing working version instead of downloading again (safer/faster)
        # We copy the parent of 'bin', which is 'runtime_node' in this case
        print(f"Copying from {current_node} to {target_dir}...")
        client.exec_command(f"cp -r {current_node} {target_dir}")
        
    # 2. Update Symlinks to point to /opt/node-v20/bin/node
    new_bin = f"{target_dir}/bin"
    
    print(f"\n--- Updating Global Links to {new_bin} ---")
    
    links = {
        "node": "/usr/bin/node",
        "npm": "/usr/bin/npm",
        "npx": "/usr/bin/npx",
        "pm2": "/usr/bin/pm2" # Also link PM2 if it's in there
    }
    
    for cmd, link_path in links.items():
        # Source path in new location
        src = f"{new_bin}/{cmd}"
        
        # Check if src exists
        stdin, stdout, stderr = client.exec_command(f"test -f {src} && echo 'yes'")
        if 'yes' in stdout.read().decode():
            client.exec_command(f"rm -f {link_path}")
            client.exec_command(f"ln -s {src} {link_path}")
            print(f"Linked {link_path} -> {src}")
            
            # Also do /usr/local/bin for safety
            local_link = f"/usr/local/bin/{cmd}"
            client.exec_command(f"rm -f {local_link}")
            client.exec_command(f"ln -s {src} {local_link}")
            print(f"Linked {local_link} -> {src}")
        else:
            print(f"Skipping {cmd} (not found in {new_bin})")

    # 3. Add to PATH in .bashrc for root
    print("\n--- Updating .bashrc PATH ---")
    path_line = f"export PATH={new_bin}:$PATH"
    # Check if already in bashrc
    stdin, stdout, stderr = client.exec_command("grep '/opt/node-v20/bin' ~/.bashrc")
    if not stdout.read():
        client.exec_command(f"echo '{path_line}' >> ~/.bashrc")
        print("Added to .bashrc")
    else:
        print("Already in .bashrc")

    # 4. Verify
    print("\n--- Verifying Node Location ---")
    stdin, stdout, stderr = client.exec_command("which node")
    print(f"Which node: {stdout.read().decode().strip()}")
    
    stdin, stdout, stderr = client.exec_command("node -v")
    print(f"Version: {stdout.read().decode().strip()}")

    client.close()

if __name__ == '__main__':
    install_node_globally()
