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
        
        # 1. Check python3-tk status
        logging.info("Checking python3-tk status...")
        stdin, stdout, stderr = client.exec_command("dpkg -l | grep python3-tk")
        out = stdout.read().decode()
        if "python3-tk" in out:
            logging.info("python3-tk is INSTALLED.")
        else:
            logging.warning("python3-tk is NOT installed. Attempting install...")
            stdin, stdout, stderr = client.exec_command("export DEBIAN_FRONTEND=noninteractive; apt-get update && apt-get install -y python3-tk")
            # Wait a bit and read
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                logging.info("python3-tk installed successfully.")
            else:
                logging.error(f"Failed to install python3-tk: {stderr.read().decode()}")

        # 2. Check for __init__.py files
        logging.info("Checking for __init__.py files...")
        paths = [
            "/var/www/sustainage/backend/__init__.py",
            "/var/www/sustainage/backend/modules/__init__.py",
            "/var/www/sustainage/backend/modules/security/__init__.py",
            "/var/www/sustainage/utils/__init__.py",
            "/var/www/sustainage/services/__init__.py"
        ]
        for p in paths:
            stdin, stdout, stderr = client.exec_command(f"ls -l {p}")
            if stdout.channel.recv_exit_status() == 0:
                logging.info(f"FOUND: {p}")
            else:
                logging.warning(f"MISSING: {p}")
                # Create it if missing
                client.exec_command(f"touch {p}")
                logging.info(f"CREATED: {p}")

        # 3. Debug RateLimiter Import
        logging.info("Debugging RateLimiter Import...")
        py_script = """
import sys
import os
sys.path.insert(0, '/var/www/sustainage')
try:
    from backend.modules.security.rate_limiter import RateLimiter
    print('SUCCESS: Imported RateLimiter')
except ImportError as e:
    print(f'FAIL: {e}')
    # List directory to see what's there
    print(f'Listing backend/modules/security: {os.listdir("/var/www/sustainage/backend/modules/security")}')
"""
        stdin, stdout, stderr = client.exec_command(f"python3 -c \"{py_script}\"")
        logging.info(f"Import Test Output:\n{stdout.read().decode()}")

        # 4. Restart Service
        logging.info("Restarting Service...")
        client.exec_command("systemctl restart sustainage")
        time.sleep(2)
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        status_out = stdout.read().decode()
        logging.info(f"Service Status (first 10 lines):\n{'\n'.join(status_out.splitlines()[:10])}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
