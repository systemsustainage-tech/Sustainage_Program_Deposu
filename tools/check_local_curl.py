import paramiko
import os

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def check_curl():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Check if key file exists
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=key_filename)
        
        print("\n--- Curl Localhost:5000 ---")
        stdin, stdout, stderr = ssh.exec_command("curl -I http://127.0.0.1:5000")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_curl()
