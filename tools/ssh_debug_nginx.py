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
        
        logging.info("Dumping Nginx Config...")
        stdin, stdout, stderr = client.exec_command("nginx -T")
        out = stdout.read().decode()
        # Filter for server blocks to keep output manageable
        # print(out) # Too long
        
        logging.info("Checking Active Config for Port 80...")
        # Just grep 'listen 80' with context
        stdin, stdout, stderr = client.exec_command("grep -r 'listen 80' /etc/nginx/")
        print(f"Grep Listen 80:\n{stdout.read().decode()}")

        logging.info("Checking Access Log...")
        stdin, stdout, stderr = client.exec_command("tail -n 10 /var/log/nginx/access.log")
        print(f"Access Log:\n{stdout.read().decode()}")
        
        logging.info("Checking Error Log...")
        stdin, stdout, stderr = client.exec_command("tail -n 10 /var/log/nginx/error.log")
        print(f"Error Log:\n{stdout.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
