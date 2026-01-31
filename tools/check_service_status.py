
import paramiko
import logging
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        # Check service status
        logging.info("Checking sustainage service status...")
        stdin, stdout, stderr = client.exec_command('systemctl status sustainage')
        logging.info(stdout.read().decode())
        logging.error(stderr.read().decode())
        
        # Check journal logs if failed
        logging.info("Checking journal logs (last 50 lines)...")
        stdin, stdout, stderr = client.exec_command('journalctl -u sustainage -n 50 --no-pager')
        logging.info(stdout.read().decode())
        
    except Exception as e:
        logging.error(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    main()
