
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def emergency_restore():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. ROLLBACK SUSTAINAGE (Reduce CPU Load)
    print("\n--- Rolling Back Sustainage Config (Low CPU Mode) ---")
    # Using minimal config to avoid CPU throttle
    # 1 worker, no threads (sync), longer timeout
    low_cpu_config = """
bind = "0.0.0.0:5000"
workers = 1
timeout = 180
loglevel = "info"
accesslog = "-"
errorlog = "-"
"""
    cmd_write = f"echo '{low_cpu_config}' > /var/www/sustainage/gunicorn_config.py"
    client.exec_command(cmd_write)
    
    print("Restarting Sustainage (Low CPU)...")
    client.exec_command("systemctl restart sustainage")

    # 2. FIX DIGAGEFINANS (Port 8003)
    # 404 means app is running but route not found.
    # Let's inspect index.js to see what it serves
    print("\n--- Inspecting DigageFinans index.js ---")
    stdin, stdout, stderr = client.exec_command("head -n 50 /root/DFinans/index.js")
    content = stdout.read().decode()
    print(content)
    
    # If it's express, look for app.get('/', ...)
    # If it's just an API, maybe we need to hit /api/status?
    
    # Also check if it's running
    client.exec_command("pm2 restart digagefinans")

    # 3. STOP TRANSFER (To save CPU)
    print("\n--- Stopping Transfer App (Saving CPU) ---")
    client.exec_command("pm2 stop transfer")
    client.exec_command("pm2 save")

    # 4. CHECK CPU LOAD
    print("\n--- Current CPU Load ---")
    stdin, stdout, stderr = client.exec_command("uptime")
    print(stdout.read().decode())

    client.close()

if __name__ == '__main__':
    emergency_restore()
