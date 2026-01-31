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
        
        # 1. Check tasks directory
        logging.info("Checking tasks directory...")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/tasks/")
        logging.info(f"Tasks Content:\n{stdout.read().decode()}")

        # 2. Check tasks/__init__.py
        stdin, stdout, stderr = client.exec_command("ls -l /var/www/sustainage/tasks/__init__.py")
        if stdout.channel.recv_exit_status() != 0:
            logging.warning("tasks/__init__.py is MISSING! Creating it...")
            client.exec_command("touch /var/www/sustainage/tasks/__init__.py")
        else:
            logging.info("tasks/__init__.py exists.")

        # 3. Grep for 'tasks' imports
        logging.info("Searching for 'import tasks' or 'from tasks'...")
        grep_cmd = "grep -r 'tasks' /var/www/sustainage/backend /var/www/sustainage/yonetim /var/www/sustainage/services"
        stdin, stdout, stderr = client.exec_command(grep_cmd)
        logging.info(f"Grep Results:\n{stdout.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
