
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def debug_sustainage_manually_v2():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. Stop Systemd Service to free port 5000
    print("\n--- Stopping Sustainage Service ---")
    client.exec_command("systemctl stop sustainage")

    # 2. Kill any lingering gunicorn process
    print("--- Killing Lingering Processes ---")
    client.exec_command("pkill -f gunicorn")
    client.exec_command("pkill -f python3") # Careful but needed if zombie

    # 3. Try Running Manually with Gunicorn (Foreground)
    print("\n--- Running Gunicorn Manually (Wait 10s) ---")
    
    # Corrected syntax: run inside bash -c
    # We redirect stderr to stdout to catch everything
    cmd_manual = 'cd /var/www/sustainage && /var/www/sustainage/venv/bin/gunicorn -w 1 -b 0.0.0.0:5000 web_app:app'
    cmd_timeout = f'timeout 10s bash -c "{cmd_manual}"'
    
    stdin, stdout, stderr = client.exec_command(cmd_timeout)
    
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    print("OUTPUT:")
    print(out)
    if err:
        print(f"STDERR: {err}")

    # 4. Check if port 5000 is listening now (if it didn't crash)
    # If timeout killed it, it won't be listening. But the output above is what matters.
    
    # 5. Restore Service
    print("\n--- Restoring Systemd Service ---")
    client.exec_command("systemctl start sustainage")

    client.close()

if __name__ == '__main__':
    debug_sustainage_manually_v2()
