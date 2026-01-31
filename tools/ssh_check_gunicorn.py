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
        
        logging.info("Checking Gunicorn Direct Response (Port 5000)...")
        stdin, stdout, stderr = client.exec_command("curl -I http://127.0.0.1:5000/login")
        out = stdout.read().decode()
        print(f"Gunicorn /login:\n{out}")
        
        logging.info("Checking Gunicorn Root Response...")
        stdin, stdout, stderr = client.exec_command("curl -I http://127.0.0.1:5000/")
        out = stdout.read().decode()
        print(f"Gunicorn /:\n{out}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
