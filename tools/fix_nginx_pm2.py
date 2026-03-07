
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def check_nginx_ports():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("\n--- Reading Nginx Configs for Ports ---")
    files = ["/etc/nginx/sites-enabled/digagefinans", "/etc/nginx/sites-enabled/digage", "/etc/nginx/sites-enabled/transfer.digage.tr"]
    
    for f in files:
        print(f"\n>>> {f}")
        stdin, stdout, stderr = client.exec_command(f"cat {f}")
        print(stdout.read().decode())

    print("\n--- Restarting PM2/Node ---")
    # Attempt to restart the Node app properly
    # 1. Kill existing node process
    print("Killing existing node processes...")
    client.exec_command("pkill -f node")
    
    # 2. Start with PM2
    print("Starting DFinans with PM2...")
    # Assuming path is /root/DFinans/index.js based on ps aux
    cmd_start = "cd /root/DFinans && pm2 start index.js --name digagefinans --port 8003"
    stdin, stdout, stderr = client.exec_command(cmd_start)
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    # 3. Save PM2 list
    client.exec_command("pm2 save")

    client.close()

if __name__ == '__main__':
    check_nginx_ports()
