import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
REMOTE_LOG_PATH = "/var/www/sustainage/backend/logs/sustainage.log"
LOCAL_LOG_PATH = "c:\\SUSTAINAGESERVER\\temp_remote_log.txt"

def fetch_log():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        sftp = ssh.open_sftp()
        
        print(f"Connected to {HOST}. Downloading {REMOTE_LOG_PATH}...")
        try:
            sftp.get(REMOTE_LOG_PATH, LOCAL_LOG_PATH)
            print(f"Log downloaded to {LOCAL_LOG_PATH}")
        except Exception as e:
            print(f"Could not download file: {e}")
            # Try to get journalctl output
            print("Trying journalctl...")
            stdin, stdout, stderr = ssh.exec_command("journalctl -u sustainage -n 50 --no-pager")
            output = stdout.read().decode()
            with open(LOCAL_LOG_PATH, "w", encoding="utf-8") as f:
                f.write(output)
            print("Journalctl output saved.")
            
        sftp.close()
        ssh.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    fetch_log()
