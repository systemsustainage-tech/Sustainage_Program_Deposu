import paramiko
import logging
import sys

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
        
        logging.info("Reading sustainage.service...")
        stdin, stdout, stderr = client.exec_command("cat /etc/systemd/system/sustainage.service")
        logging.info(f"Service Def:\n{stdout.read().decode()}")
        
        logging.info("Checking Gunicorn User...")
        stdin, stdout, stderr = client.exec_command("ps aux | grep gunicorn")
        logging.info(f"Processes:\n{stdout.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
