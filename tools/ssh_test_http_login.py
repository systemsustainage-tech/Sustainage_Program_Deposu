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
        
        logging.info("Testing login via HTTP POST...")
        # curl -c cookies.txt -b cookies.txt -d "username=__super__&password=super123" -X POST http://127.0.0.1:5000/login -L -v
        cmd = 'curl -c cookies.txt -b cookies.txt -d "username=__super__&password=super123" -X POST http://127.0.0.1:5000/login -L -i'
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print(f"Output:\n{out}")
        print(f"Error:\n{err}")
        
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
