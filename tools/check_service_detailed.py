import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_service():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        print("\n--- Service Status ---")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        print(stdout.read().decode())
        
        print("\n--- Gunicorn Processes ---")
        stdin, stdout, stderr = client.exec_command("ps aux | grep gunicorn")
        print(stdout.read().decode())

        print("\n--- Recent Logs (Errors) ---")
        # Grep for error/exception/traceback
        cmd = "journalctl -u sustainage -n 200 --no-pager | grep -iE 'error|exception|traceback' | tail -n 20"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())

    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_service()
