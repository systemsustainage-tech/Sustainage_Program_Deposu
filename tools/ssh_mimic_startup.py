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
        
        py_script = """
import sys
import os
import logging

# Mimic web_app.py startup
ROOT_DIR = '/var/www/sustainage'
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

print(f"sys.path: {sys.path}")

print("--- Testing 'import tasks' ---")
try:
    import tasks
    print(f"SUCCESS: tasks imported from {tasks.__file__}")
except ImportError as e:
    print(f"FAIL: import tasks: {e}")

print("--- Testing 'from tasks.email_service import EmailService' ---")
try:
    from tasks.email_service import EmailService
    print("SUCCESS: EmailService imported")
except ImportError as e:
    print(f"FAIL: from tasks.email_service: {e}")

print("--- Testing 'import backend' ---")
try:
    import backend
    print(f"SUCCESS: backend imported from {backend.__file__}")
except ImportError as e:
    print(f"FAIL: import backend: {e}")

print("--- Testing 'from backend.modules.security.rate_limiter import RateLimiter' ---")
try:
    from backend.modules.security.rate_limiter import RateLimiter
    print("SUCCESS: RateLimiter imported")
except ImportError as e:
    print(f"FAIL: RateLimiter import: {e}")

"""
        logging.info("Running import simulation...")
        stdin, stdout, stderr = client.exec_command(f"python3 -c \"{py_script}\"")
        out = stdout.read().decode()
        err = stderr.read().decode()
        logging.info(f"Output:\n{out}")
        if err:
            logging.info(f"Error:\n{err}")

        logging.info("Checking permissions...")
        client.exec_command("ls -ld /var/www/sustainage/tasks")
        client.exec_command("ls -l /var/www/sustainage/tasks/__init__.py")
        client.exec_command("ls -ld /var/www/sustainage/backend")
        
        stdin, stdout, stderr = client.exec_command("namei -l /var/www/sustainage/tasks/email_service.py")
        logging.info(f"Permissions Check:\n{stdout.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
