import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_logs():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    connected = False
    for attempt in range(3):
        try:
            print(f"Connecting to {HOSTNAME} (Attempt {attempt+1}/3)...")
            client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, banner_timeout=30)
            connected = True
            break
        except Exception as e:
            print(f"Connection failed: {e}")
            import time
            time.sleep(2)
            
    if not connected:
        print("Could not connect after 3 attempts.")
        return

    try:
        print("Fetching logs...")
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())
        print(stderr.read().decode())
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_logs()
