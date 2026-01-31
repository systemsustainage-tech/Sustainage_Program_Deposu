import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_fix_users():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Run fix_users.py
        # Need to set PYTHONPATH or run from correct dir
        cmd = 'cd /var/www/sustainage && python3 tools/fix_users.py'
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("--- STDOUT ---")
        print(out)
        print("--- STDERR ---")
        print(err)

        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    run_fix_users()
