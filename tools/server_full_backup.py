
import paramiko
import os
import sys
import time

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def create_full_backup():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    timestamp = int(time.time())
    backup_dir = f"/root/BACKUPS/full_backup_{timestamp}"
    
    print(f"\n--- Creating Backup Directory: {backup_dir} ---")
    client.exec_command(f"mkdir -p {backup_dir}")

    # 1. Backup Sustainage (Code + DB)
    print(">>> Backing up Sustainage...")
    # Exclude venv and __pycache__ to save space/time
    cmd_sustainage = f"tar --exclude='venv' --exclude='__pycache__' -czf {backup_dir}/sustainage.tar.gz -C /var/www sustainage"
    stdin, stdout, stderr = client.exec_command(cmd_sustainage)
    if stderr.read():
        print("Warning during Sustainage backup (might be file change warnings)")

    # 2. Backup DigageFinans
    print(">>> Backing up DigageFinans...")
    cmd_df = f"tar --exclude='node_modules' -czf {backup_dir}/digagefinans.tar.gz -C /root DFinans"
    client.exec_command(cmd_df)

    # 3. Backup Transfer App
    print(">>> Backing up Transfer App...")
    # Assuming it's at /var/www/DIGAGETRANSFER as found earlier
    cmd_tr = f"tar --exclude='node_modules' -czf {backup_dir}/transfer.tar.gz -C /var/www DIGAGETRANSFER"
    client.exec_command(cmd_tr)
    
    # 4. Backup Nginx Configs
    print(">>> Backing up Nginx Configs...")
    client.exec_command(f"cp -r /etc/nginx/sites-available {backup_dir}/nginx_sites")
    
    # 5. List Backup Contents
    print("\n--- Backup Completed ---")
    stdin, stdout, stderr = client.exec_command(f"ls -lh {backup_dir}")
    print(stdout.read().decode())
    
    print(f"Backup stored at: {backup_dir}")

    client.close()

if __name__ == '__main__':
    create_full_backup()
