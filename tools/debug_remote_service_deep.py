
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_debug_commands():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Get more lines to find the python traceback
    commands = [
        "journalctl -u sustainage -n 200 --no-pager"
    ]
    
    for cmd in commands:
        print(f"\n--- Running: {cmd} ---")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode().strip()
        
        if out:
            print(out)

    client.close()

if __name__ == '__main__':
    run_debug_commands()
