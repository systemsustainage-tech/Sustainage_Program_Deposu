import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

REMOTE_PATH = '/var/www/sustainage/tools/fix_users.py'

def check_remote_fix_users():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        stdin, stdout, stderr = client.exec_command(f'cat {REMOTE_PATH}')
        content = stdout.read().decode()
        
        print(f"--- Content of {REMOTE_PATH} ---")
        if "INSERT INTO users" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "INSERT INTO users" in line:
                    for j in range(i, min(i + 10, len(lines))):
                        print(f"{j+1}: {lines[j]}")
                    break
        else:
            print("INSERT statement not found.")
            
        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_remote_fix_users()
