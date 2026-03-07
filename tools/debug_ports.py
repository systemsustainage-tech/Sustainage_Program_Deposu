
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = "C:\\Users\\Trae\\.ssh\\id_rsa"
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def deep_debug():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 1. Check Local Ports (Is app listening?)
    print("\n--- Checking Local Ports (netstat) ---")
    stdin, stdout, stderr = client.exec_command("netstat -tuln | grep LISTEN")
    print(stdout.read().decode())

    # 2. Test Local Responses (curl)
    ports = [5000, 8002, 8003]
    print("\n--- Testing Local Responses (curl localhost:PORT) ---")
    for p in ports:
        print(f"Testing Port {p}...")
        # Timeout 5s, head only
        cmd = f"curl -I -m 5 http://127.0.0.1:{p}"
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out:
            print(f"[{p}] RESPONSE:\n{out}")
        else:
            print(f"[{p}] NO RESPONSE. Error: {err}")

    # 3. Check Nginx Logs for Recent Errors
    print("\n--- Nginx Error Log (Last 20 lines) ---")
    stdin, stdout, stderr = client.exec_command("tail -n 20 /var/log/nginx/error.log")
    print(stdout.read().decode())

    # 4. Check PM2 Logs for App Errors
    print("\n--- PM2 Logs (Last 20 lines) ---")
    # digagefinans
    print(">>> digagefinans logs:")
    client.exec_command("pm2 logs digagefinans --lines 20 --nostream") # This might hang, use read
    stdin, stdout, stderr = client.exec_command("tail -n 20 /root/.pm2/logs/digagefinans-error.log")
    print(stdout.read().decode())
    
    print(">>> transfer logs:")
    stdin, stdout, stderr = client.exec_command("tail -n 20 /root/.pm2/logs/transfer-error.log")
    print(stdout.read().decode())

    client.close()

if __name__ == '__main__':
    deep_debug()
