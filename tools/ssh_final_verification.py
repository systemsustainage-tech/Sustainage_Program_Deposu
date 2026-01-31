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
        
        logging.info("Checking /etc/hosts...")
        stdin, stdout, stderr = client.exec_command("cat /etc/hosts")
        print(stdout.read().decode())
        
        logging.info("Checking UFW status...")
        stdin, stdout, stderr = client.exec_command("ufw status")
        print(stdout.read().decode())
        
        logging.info("Checking Nginx Access Logs (Last 10)...")
        stdin, stdout, stderr = client.exec_command("tail -n 10 /var/log/nginx/access.log")
        print(stdout.read().decode())
        
        logging.info("Checking Nginx Error Logs (Last 10)...")
        stdin, stdout, stderr = client.exec_command("tail -n 10 /var/log/nginx/error.log")
        print(stdout.read().decode())

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
