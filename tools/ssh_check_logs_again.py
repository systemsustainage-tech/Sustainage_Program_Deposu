import paramiko
import logging
import sys
import time

# Configuration
HOST = '72.62.150.207'
PORT = 22
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Checking logs for recent errors (last 50 lines)...")
        stdin, stdout, stderr = client.exec_command("tail -n 50 /var/www/sustainage/logs/error.log")
        logging.info(f"Error Log:\n{stdout.read().decode()}")

        logging.info("Checking service status again...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        logging.info(f"Service Status:\n{stdout.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
