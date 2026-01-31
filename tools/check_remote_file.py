import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

REMOTE_PATH = '/var/www/sustainage/backend/yonetim/kullanici_yonetimi/models/user_manager.py'

def check_remote_file():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        stdin, stdout, stderr = client.exec_command(f'cat {REMOTE_PATH}')
        content = stdout.read().decode()
        
        print(f"--- Content of {REMOTE_PATH} ---")
        # Print first 100 lines or search for specific strings
        if "DEBUG: Auth attempt" in content:
            print("FOUND: 'DEBUG: Auth attempt' string in file.")
        else:
            print("NOT FOUND: 'DEBUG: Auth attempt' string in file.")
            
        print("-" * 20)
        # Print the authenticate method part
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "def authenticate" in line:
                for j in range(i, min(i + 40, len(lines))):
                    print(f"{j+1}: {lines[j]}")
                break
                
        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_remote_file()
