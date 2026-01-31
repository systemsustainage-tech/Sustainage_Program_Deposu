import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'
REMOTE_BASE_DIR = '/var/www/sustainage'

def restart_app():
    print("Restarting remote application...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Method 1: Touch restart.txt (Passenger)
        print("Touching tmp/restart.txt...")
        client.exec_command(f"mkdir -p {REMOTE_BASE_DIR}/tmp")
        client.exec_command(f"touch {REMOTE_BASE_DIR}/tmp/restart.txt")
        
        # Method 2: Check for systemd service and restart if exists
        stdin, stdout, stderr = client.exec_command("systemctl list-units --type=service | grep sustainage")
        service_info = stdout.read().decode()
        if service_info:
            print("Found systemd service, restarting...")
            client.exec_command("systemctl restart sustainage")
        else:
            print("No specific 'sustainage' service found. Assuming Passenger restart is enough.")
            
        print("Restart signal sent.")
        
    except Exception as e:
        print(f"Error restarting app: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    restart_app()
