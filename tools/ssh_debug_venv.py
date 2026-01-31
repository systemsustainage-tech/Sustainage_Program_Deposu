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
        
        # 1. Check venv python imports
        logging.info("Running debug script with VENV python...")
        stdin, stdout, stderr = client.exec_command("/var/www/sustainage/venv/bin/python3 /var/www/sustainage/debug_imports.py")
        out = stdout.read().decode()
        err = stderr.read().decode()
        logging.info(f"Output:\n{out}")
        if err:
            logging.info(f"Error:\n{err}")

        # 2. Check if venv sees tkinter
        logging.info("Checking tkinter in VENV...")
        cmd = "/var/www/sustainage/venv/bin/python3 -c 'import tkinter; print(tkinter)'"
        stdin, stdout, stderr = client.exec_command(cmd)
        logging.info(f"Tkinter Check:\n{stdout.read().decode()}")
        logging.info(f"Tkinter Error:\n{stderr.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
