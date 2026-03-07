
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def debug_sustainage_manually():
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
    # This will show us the REAL error immediately
    print("\n--- Running Gunicorn Manually (First 20 lines of output) ---")
    
    # We use a timeout to not block forever, just catch startup error
    cmd_manual = "cd /var/www/sustainage && /var/www/sustainage/venv/bin/gunicorn -w 1 -b 0.0.0.0:5000 web_app:app"
    
    # We execute this and read stderr
    # Note: exec_command returns immediately, reading stdout blocks.
    # But if gunicorn runs, it blocks. So we need a way to peek.
    # Let's run with timeout 10s and capture output
    cmd_timeout = f"timeout 10s {cmd_manual}"
    
    stdin, stdout, stderr = client.exec_command(cmd_timeout)
    
    print("STDOUT:")
    print(stdout.read().decode())
    print("STDERR:")
    print(stderr.read().decode())

    # 4. Check if port 5000 is listening now (if it didn't crash)
    print("\n--- Checking Port 5000 ---")
    stdin, stdout, stderr = client.exec_command("netstat -tuln | grep :5000")
    print(stdout.read().decode())

    # 5. If successful manually, update systemd and restart
    # But first let's see the error.

    client.close()

if __name__ == '__main__':
    debug_sustainage_manually()
