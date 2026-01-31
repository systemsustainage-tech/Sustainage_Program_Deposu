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
        
        # 1. List tasks
        logging.info("Listing tasks directory...")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/tasks/")
        logging.info(f"Tasks:\n{stdout.read().decode()}")

        # 2. Read rate_limiter.py
        logging.info("Reading rate_limiter.py...")
        stdin, stdout, stderr = client.exec_command("cat /var/www/sustainage/backend/modules/security/rate_limiter.py")
        logging.info(f"RateLimiter Content:\n{stdout.read().decode()}")

        # 3. Read email_service.py
        logging.info("Reading email_service.py...")
        stdin, stdout, stderr = client.exec_command("cat /var/www/sustainage/services/email_service.py")
        logging.info(f"EmailService Content:\n{stdout.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
