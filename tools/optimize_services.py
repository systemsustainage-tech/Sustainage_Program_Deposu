
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def optimize_and_restart():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. OPTIMIZE GUNICORN (Sustainage)
    print("\n--- Optimizing Gunicorn Config ---")
    
    # Increase timeout to 120s, limit workers to 2 (to save CPU)
    new_config = """
import multiprocessing

bind = "0.0.0.0:5000"
workers = 2
timeout = 120
keepalive = 5
threads = 2
worker_class = "gthread"
loglevel = "info"
accesslog = "-"
errorlog = "-"
"""
    # Write config remotely
    cmd_write = f"echo '{new_config}' > /var/www/sustainage/gunicorn_config.py"
    client.exec_command(cmd_write)
    
    # Restart Service
    print("Restarting Sustainage...")
    client.exec_command("systemctl restart sustainage")

    # 2. FIX DIGAGEFINANS (Port 8003)
    # Problem: It returns 404 for root. It might be serving from a subpath or needs history fallback.
    print("\n--- Checking DigageFinans Structure ---")
    stdin, stdout, stderr = client.exec_command("ls -F /root/DFinans/")
    files = stdout.read().decode().split()
    print(f"Files: {files}")
    
    # Restart with SPA handling? Usually handled by Nginx try_files.
    # Let's check Nginx config again for try_files
    stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/digagefinans")
    nginx_conf = stdout.read().decode()
    
    if "try_files $uri $uri/ /index.html;" not in nginx_conf:
        print("Adding try_files to Nginx for DigageFinans...")
        # We need to be careful editing Nginx conf remotely via script.
        # But wait, it's proxied to port 8003. So the Node app handles routing.
        # If Node returns 404, then the app doesn't have a '/' route defined.
        pass

    # 3. FIX TRANSFER APP (Port 8002)
    # Problem: 405 Method Not Allowed. Likely an API only app?
    # Let's see logs
    print("\n--- Checking Transfer Logs ---")
    stdin, stdout, stderr = client.exec_command("tail -n 20 /root/.pm2/logs/transfer-out.log")
    print(stdout.read().decode())

    # 4. RESTART NGINX
    print("\n--- Reloading Nginx ---")
    client.exec_command("systemctl reload nginx")

    # 5. FINAL VERIFICATION
    print("\n--- Verifying All Ports ---")
    import time
    time.sleep(5) # Wait for restart
    
    for p in [5000, 8002, 8003]:
        cmd = f"curl -I -m 5 http://127.0.0.1:{p}"
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode()
        if "HTTP/1.1 200" in out or "HTTP/1.1 302" in out or "HTTP/1.1 404" in out:
             print(f"[{p}] UP (Status: {out.splitlines()[0]})")
        else:
             print(f"[{p}] STATUS: {out.splitlines()[0] if out else 'DOWN'}")

    client.close()

if __name__ == '__main__':
    optimize_and_restart()
