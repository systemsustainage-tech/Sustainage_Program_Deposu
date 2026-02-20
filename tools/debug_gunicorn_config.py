import paramiko
import os

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def read_remote_file():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Check if key file exists
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=key_filename)
        
        print("\n--- gunicorn_config.py ---")
        stdin, stdout, stderr = ssh.exec_command("cat /var/www/sustainage/gunicorn_config.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\n--- systemctl status sustainage ---")
        # Force strict output
        stdin, stdout, stderr = ssh.exec_command("systemctl status sustainage --no-pager")
        print(stdout.read().decode())
        print(stderr.read().decode())

        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    read_remote_file()
