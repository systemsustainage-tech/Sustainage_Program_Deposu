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
        
        # 1. Install python3-tk
        logging.info("Installing python3-tk...")
        stdin, stdout, stderr = client.exec_command("apt-get update && apt-get install -y python3-tk")
        out = stdout.read().decode()
        err = stderr.read().decode()
        logging.info(f"Install Output (last 5 lines):\n{'\n'.join(out.splitlines()[-5:])}")
        if err:
            logging.info(f"Install Stderr:\n{err}")

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

        # 3. Check imports in dependencies
        logging.info("Checking for tkinter in dependencies...")
        grep_cmd = "grep -r 'tkinter' /var/www/sustainage/utils /var/www/sustainage/services /var/www/sustainage/yonetim"
        stdin, stdout, stderr = client.exec_command(grep_cmd)
        logging.info(f"Grep Results:\n{stdout.read().decode()}")

        # 4. Debug RateLimiter Import
        logging.info("Debugging RateLimiter Import...")
        py_script = """
import sys
import os
sys.path.insert(0, '/var/www/sustainage')
print(f'Sys Path: {sys.path}')
try:
    from backend.modules.security.rate_limiter import RateLimiter
    print('SUCCESS: Imported RateLimiter from backend.modules.security.rate_limiter')
except ImportError as e:
    print(f'FAIL 1: {e}')
    try:
        from modules.security.rate_limiter import RateLimiter
        print('SUCCESS: Imported RateLimiter from modules.security.rate_limiter')
    except ImportError as e2:
        print(f'FAIL 2: {e2}')
"""
        stdin, stdout, stderr = client.exec_command(f"python3 -c \"{py_script}\"")
        logging.info(f"Import Test Output:\n{stdout.read().decode()}")
        logging.info(f"Import Test Error:\n{stderr.read().decode()}")

        # 5. Restart Service
        logging.info("Restarting Service...")
        client.exec_command("systemctl restart sustainage")
        time.sleep(2)
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        logging.info(f"Service Status:\n{stdout.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
