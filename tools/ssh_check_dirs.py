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
        
        logging.info("--- CHECKING DIRECTORIES ---")
        
        logging.info("ls -F /var/www/sustainage/")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/")
        print(stdout.read().decode())
        
        logging.info("ls -F /var/www/sustainage/SDG_WEB/")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/SDG_WEB/")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print(f"STDOUT:\n{out}")
        print(f"STDERR:\n{err}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
