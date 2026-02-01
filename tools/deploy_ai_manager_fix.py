import paramiko
import os
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

LOCAL_FILE = "c:/SUSTAINAGESERVER/backend/modules/ai/ai_manager.py"
REMOTE_FILE = "/var/www/sustainage/backend/modules/ai/ai_manager.py"

def deploy_ai_fix():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        print(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        sftp.close()
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        time.sleep(5)
        
        print("Checking status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage.service -n 20 --no-pager")
        print("--- Recent Logs ---")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_ai_fix()
