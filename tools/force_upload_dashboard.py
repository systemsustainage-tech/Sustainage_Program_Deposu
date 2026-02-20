import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

LOCAL_FILE = r"c:\SUSTAINAGESERVER\backend\modules\data_inventory\advanced_dashboard.py"
REMOTE_FILE = "/var/www/sustainage/backend/modules/data_inventory/advanced_dashboard.py"

def upload_file():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        client.connect(HOST, username=USER, key_filename=key_filename)
        
        sftp = client.open_sftp()
        print(f"Uploading {LOCAL_FILE} -> {REMOTE_FILE}")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        print("Upload successful.")
        
        # Verify remote file size/content head
        stdin, stdout, stderr = client.exec_command(f"head -n 305 {REMOTE_FILE} | tail -n 10")
        print("\n--- Remote File Check (Lines 296-305) ---")
        print(stdout.read().decode())
        
        sftp.close()
        client.close()
        
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    upload_file()
