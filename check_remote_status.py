import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_status():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, username=USER, password=PASS)
        
        print("--- Systemctl Status ---")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        
        print("\n--- Process List ---")
        stdin, stdout, stderr = client.exec_command("ps aux | grep web_app.py | grep -v grep")
        print(stdout.read().decode())
        
        print("\n--- Last 50 lines of Log ---")
        # Check both potential log locations
        stdin, stdout, stderr = client.exec_command("tail -n 50 /var/www/sustainage/app.log")
        print(stdout.read().decode())
        
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())
        
    finally:
        client.close()

if __name__ == "__main__":
    check_status()
