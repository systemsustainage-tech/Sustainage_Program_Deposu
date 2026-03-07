
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def install_clean_node():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. Download and Install Node.js v20 (LTS)
    print("\n--- Downloading Node.js v20 ---")
    # Using nodesource setup script which is standard for Ubuntu
    cmd_install = "curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs"
    
    # Run setup
    stdin, stdout, stderr = client.exec_command(cmd_install)
    # Stream output to see progress
    for line in stdout:
        print(line.strip())
    err = stderr.read().decode()
    if err:
        print(f"STDERR: {err}")

    # 2. Verify Installation
    print("\n--- Verifying Node & NPM ---")
    stdin, stdout, stderr = client.exec_command("node -v && npm -v")
    print(stdout.read().decode())

    # 3. Install PM2 Globally
    print("\n--- Installing PM2 Globally ---")
    stdin, stdout, stderr = client.exec_command("npm install -g pm2")
    print(stdout.read().decode())

    # 4. Restart Apps
    print("\n--- Restarting Apps with Fresh PM2 ---")
    
    # DigageFinans
    cmd_df = "cd /root/DFinans && PORT=8003 pm2 start index.js --name digagefinans --force"
    print(f"Running: {cmd_df}")
    client.exec_command(cmd_df)
    
    # Transfer App (Try finding it again or use previous knowledge)
    # We'll assume /var/www/transfer or similar. Let's try finding it dynamically again to be safe
    stdin, stdout, stderr = client.exec_command("find /var/www /root -name package.json -maxdepth 3 | grep transfer")
    transfer_pkg = stdout.read().decode().strip()
    
    if transfer_pkg:
        transfer_dir = os.path.dirname(transfer_pkg)
        print(f"Found Transfer App at: {transfer_dir}")
        # Check start script
        cmd_transfer = f"cd {transfer_dir} && PORT=8002 pm2 start npm --name transfer -- start --force"
        client.exec_command(cmd_transfer)
        print("Started Transfer App")
    else:
        print("Could not auto-locate Transfer App. Please check path manually.")

    # Save
    client.exec_command("pm2 save")
    client.exec_command("pm2 list")
    
    client.close()

if __name__ == '__main__':
    install_clean_node()
