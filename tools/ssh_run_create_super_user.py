import paramiko
import logging
import sys
import os

# Configuration
HOST = '72.62.150.207'
PORT = 22
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
LOCAL_FILE = 'c:/SDG/tools/create_super_user_remote.py'
REMOTE_FILE = '/var/www/sustainage/create_super_user.py'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        sftp = client.open_sftp()

        logging.info(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        
        logging.info("Running script...")
        # Use venv python to ensure argon2 is available
        stdin, stdout, stderr = client.exec_command(f"/var/www/sustainage/venv/bin/python3 {REMOTE_FILE}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
