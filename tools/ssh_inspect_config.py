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
        
        commands = [
            "systemctl status sustainage --no-pager",
            "cat /etc/nginx/sites-enabled/default",
            "cat /etc/nginx/sites-enabled/sustainage", 
            "ls -F /etc/nginx/sites-enabled/",
            "cat /etc/systemd/system/sustainage.service",
            "journalctl -u sustainage -n 50 --no-pager"
        ]
        
        for cmd in commands:
            logging.info(f"--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode()
            err = stderr.read().decode()
            logging.info(f"Output:\n{out}")
            if err:
                logging.warning(f"Error:\n{err}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
