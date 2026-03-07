
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def investigate_and_fix_all():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. FIX SUSTAINAGE (Systemd Service)
    print("\n=== Fixing Sustainage Service ===")
    
    # Check Logs
    print(">>> Reading Logs...")
    stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
    logs = stdout.read().decode()
    print(logs)
    
    # Possible fix: If it's a timeout issue, extend TimeoutStartSec in systemd
    # But first, let's try to restart it cleanly
    client.exec_command("systemctl stop sustainage")
    client.exec_command("systemctl reset-failed sustainage")
    client.exec_command("systemctl start sustainage")
    
    # 2. FIX PM2 APPS (DigageFinans & Transfer)
    print("\n=== Fixing PM2 Apps ===")
    
    # Ensure PM2 is running (resurrect if possible, else start fresh)
    client.exec_command("pm2 resurrect") 
    
    # DigageFinans (Port 8003)
    print(">>> Starting DigageFinans...")
    # Using 'npm start' usually better than 'node index.js' for robust apps
    # But stick to what worked: index.js
    cmd_df = "cd /root/DFinans && PORT=8003 pm2 start index.js --name digagefinans --force"
    client.exec_command(cmd_df)
    
    # Transfer App (Port 8002) - AGGRESSIVE SEARCH
    print(">>> Searching & Starting Transfer App...")
    
    # List all directories in /var/www to find it manually
    stdin, stdout, stderr = client.exec_command("ls -F /var/www/")
    dirs = stdout.read().decode().split()
    print(f"Directories in /var/www: {dirs}")
    
    transfer_path = None
    for d in dirs:
        if 'transfer' in d.lower():
            transfer_path = f"/var/www/{d.rstrip('/')}"
            break
    
    if not transfer_path:
        # Check root
        stdin, stdout, stderr = client.exec_command("ls -F /root/")
        dirs_root = stdout.read().decode().split()
        for d in dirs_root:
            if 'transfer' in d.lower():
                transfer_path = f"/root/{d.rstrip('/')}"
                break

    if transfer_path:
        print(f"FOUND Transfer App at: {transfer_path}")
        # Try to start it
        cmd_tr = f"cd {transfer_path} && PORT=8002 pm2 start npm --name transfer -- start --force"
        client.exec_command(cmd_tr)
    else:
        print("CRITICAL: Transfer App folder NOT found. Cannot start.")

    # 3. SAVE PM2 STATE
    print(">>> Saving PM2 List...")
    client.exec_command("pm2 save")
    # Generate startup script just in case
    client.exec_command("pm2 startup systemd -u root --hp /root")

    # 4. FINAL STATUS
    print("\n=== Final Status Report ===")
    stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
    print(f"Sustainage: {stdout.read().decode()}")
    
    stdin, stdout, stderr = client.exec_command("pm2 list")
    print(f"PM2 Apps:\n{stdout.read().decode()}")

    client.close()

if __name__ == '__main__':
    investigate_and_fix_all()
