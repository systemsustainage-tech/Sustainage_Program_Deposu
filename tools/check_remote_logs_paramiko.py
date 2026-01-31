import paramiko
import time

def check_logs():
    host = "72.62.150.207"
    username = "root"
    password = "Kayra_1507"
    
    print(f"Connecting to {host}...")
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)
        
        print("Checking service status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        
        print("\nChecking journal logs (last 200 lines)...")
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 200 --no-pager")
        print(stdout.read().decode())
        
        print("\nChecking nginx error logs (last 20 lines)...")
        stdin, stdout, stderr = client.exec_command("tail -n 20 /var/log/nginx/error.log")
        print(stdout.read().decode())
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_logs()
