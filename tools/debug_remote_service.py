
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"  # Adjust if needed, or rely on agent
# Try standard paths if specific one not found
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

    commands = [
        "systemctl status sustainage --no-pager",
        "journalctl -u sustainage -n 50 --no-pager",
        "tail -n 20 /var/log/nginx/error.log"
    ]
    
    for cmd in commands:
        print(f"\n--- Running: {cmd} ---")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        if out:
            print(out)
        if err:
            print(f"STDERR: {err}")

    client.close()

if __name__ == '__main__':
    run_debug_commands()
