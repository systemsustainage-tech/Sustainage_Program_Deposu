import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def mkdir_remote(path):
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
        stdin, stdout, stderr = client.exec_command(f'mkdir -p {path}')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"Successfully created directory: {path}")
        else:
            print(f"Error creating directory: {stderr.read().decode()}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remote_mkdir.py <path>")
        sys.exit(1)
    mkdir_remote(sys.argv[1])
