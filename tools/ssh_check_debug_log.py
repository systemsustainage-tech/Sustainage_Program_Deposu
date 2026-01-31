
import paramiko
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

REMOTE_LOG_FILE = '/var/www/sustainage/logs/web_app_debug.log'

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info(f"Reading {REMOTE_LOG_FILE}...")
        stdin, stdout, stderr = client.exec_command(f"cat {REMOTE_LOG_FILE}")
        content = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if content:
            print("\n--- DEBUG LOG CONTENT ---\n")
            print(content)
            print("\n-------------------------\n")
        else:
            logging.warning("Log file is empty or does not exist.")
            if error:
                logging.error(f"Error reading log: {error}")
                
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
