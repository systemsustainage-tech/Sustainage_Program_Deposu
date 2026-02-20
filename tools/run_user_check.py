import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
REMOTE_PATH = "/var/www/sustainage/tools/check_user_details.py"
LOCAL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "check_user_details.py"))

def run_check():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {HOST}...")
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        # Upload
        sftp = ssh.open_sftp()
        print(f"Uploading {LOCAL_PATH} to {REMOTE_PATH}...")
        sftp.put(LOCAL_PATH, REMOTE_PATH)
        sftp.close()
        
        # Execute
        print("Running user check...")
        cmd = "cd /var/www/sustainage && source venv/bin/activate && python tools/check_user_details.py super.admin"
        stdin, stdout, stderr = ssh.exec_command(f"bash -c '{cmd}'")
        
        print("--- STDOUT ---")
        print(stdout.read().decode())
        print("--- STDERR ---")
        print(stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_check()
