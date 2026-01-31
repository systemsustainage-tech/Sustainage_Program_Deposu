import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_remote_dirs():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Check if 'yonetim' exists in root
        stdin, stdout, stderr = client.exec_command('ls -d /var/www/sustainage/yonetim')
        if stdout.read():
            print("FOUND: /var/www/sustainage/yonetim exists!")
        else:
            print("NOT FOUND: /var/www/sustainage/yonetim does not exist.")
            
        # Check if 'backend/yonetim' exists
        stdin, stdout, stderr = client.exec_command('ls -d /var/www/sustainage/backend/yonetim')
        if stdout.read():
            print("FOUND: /var/www/sustainage/backend/yonetim exists!")
        else:
            print("NOT FOUND: /var/www/sustainage/backend/yonetim does not exist.")

        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_remote_dirs()
