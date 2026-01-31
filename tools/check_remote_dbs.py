import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_remote_dbs():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        paths = [
            '/var/www/sustainage/sustainage.db',
            '/var/www/sustainage/backend/data/sdg_desktop.sqlite',
            '/var/www/sustainage/backend/data/sustainage.db'
        ]
        
        for path in paths:
            stdin, stdout, stderr = client.exec_command(f'ls -l {path}')
            out = stdout.read().decode().strip()
            if out:
                print(f"FOUND: {out}")
            else:
                print(f"NOT FOUND: {path}")

        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check_remote_dbs()
