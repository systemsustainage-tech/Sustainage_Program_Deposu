import paramiko
import time

def restart_and_check():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Waiting 5 seconds...")
        time.sleep(5)
        
        print("Checking status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        
        print("Checking recent logs (last 50 lines)...")
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    restart_and_check()
