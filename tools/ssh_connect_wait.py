import paramiko
import logging
import sys

# Configuration
HOST = '72.62.150.207'
PORT = 22
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_DIR = '/var/www/sustainage'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info(f"Checking directory {REMOTE_DIR}...")
        stdin, stdout, stderr = client.exec_command(f"ls -la {REMOTE_DIR}")
        print(stdout.read().decode())
        
        logging.info("Checking sustainage service status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())

        client.close()
        logging.info("Connection successful. Waiting for instructions.")

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
