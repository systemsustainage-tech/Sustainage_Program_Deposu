import os
import shutil
import paramiko
import time

# Configuration
HOST = "72.62.150.207"
USER = "root"
PASS = "Sustain_2024!"
REMOTE_BASE = "/var/www/sustainage"

def sync_local_translations():
    print("Syncing local translations...")
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = os.path.join(root_dir, 'locales', 'tr.json')
    dst = os.path.join(root_dir, 'backend', 'locales', 'tr.json')
    
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Copied {src} to {dst}")
    else:
        print(f"Source not found: {src}")

    # Also sync en.json
    src_en = os.path.join(root_dir, 'locales', 'en.json')
    dst_en = os.path.join(root_dir, 'backend', 'locales', 'en.json')
    if os.path.exists(src_en):
        shutil.copy2(src_en, dst_en)
        print(f"Copied {src_en} to {dst_en}")

def deploy_fixes():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()

        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 1. Deploy web_app.py (Survey fix)
        local_webapp = os.path.join(root_dir, 'web_app.py')
        remote_webapp = f"{REMOTE_BASE}/web_app.py"
        print(f"Uploading {local_webapp} to {remote_webapp}...")
        sftp.put(local_webapp, remote_webapp)

        # 2. Deploy translations to BOTH locations
        files_to_sync = [
            ('locales/tr.json', 'locales/tr.json'),
            ('locales/tr.json', 'backend/locales/tr.json'),
            ('locales/en.json', 'locales/en.json'),
            ('locales/en.json', 'backend/locales/en.json'),
        ]

        for local_rel, remote_rel in files_to_sync:
            # Note: local source is always root/locales/tr.json because we synced it there
            # Wait, for the second item, I want to upload root/locales/tr.json to remote/backend/locales/tr.json
            local_path = os.path.join(root_dir, 'locales', 'tr.json' if 'tr.json' in local_rel else 'en.json')
            remote_path = f"{REMOTE_BASE}/{remote_rel}"
            
            print(f"Uploading {local_path} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
            except IOError:
                # Directory might not exist
                remote_dir = os.path.dirname(remote_path)
                print(f"Ensuring directory exists: {remote_dir}")
                ssh.exec_command(f"mkdir -p {remote_dir}")
                sftp.put(local_path, remote_path)

        # 3. Restart Service
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Failed to restart service: {stderr.read().decode()}")

        sftp.close()
        ssh.close()
        print("Sync and deploy complete.")

    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    sync_local_translations()
    deploy_fixes()
