import paramiko
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def diagnose():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        
        print("--- 1. Systemctl Status ---")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\n--- 2. Journalctl Logs (Last 20) ---")
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 20 --no-pager")
        print(stdout.read().decode())
        
        print("\n--- 3. App Log (Last 20) ---")
        stdin, stdout, stderr = client.exec_command("tail -n 20 /var/www/sustainage/app.log")
        print(stdout.read().decode())

        print("\n--- 4. Python Processes ---")
        stdin, stdout, stderr = client.exec_command("ps aux | grep python")
        print(stdout.read().decode())

        print("\n--- 5. Nginx Config (Upstream) ---")
        # Trying to find where nginx sends requests. Usually in default or sustainage file
        stdin, stdout, stderr = client.exec_command("grep -r 'proxy_pass' /etc/nginx/sites-enabled/")
        print(stdout.read().decode())
        
        print("\n--- 6. Listening Ports ---")
        stdin, stdout, stderr = client.exec_command("netstat -tulnp | grep python")
        print(stdout.read().decode())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    diagnose()
