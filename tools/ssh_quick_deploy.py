
import paramiko
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

REMOTE_BASE = '/var/www/sustainage'
LOCAL_FILE = 'c:/SDG/server/web_app.py'
REMOTE_FILE = f'{REMOTE_BASE}/web_app.py'

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        sftp = client.open_sftp()
        logging.info("Connected.")
        
        logging.info(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        sftp.chmod(REMOTE_FILE, 0o755)
        logging.info("Upload complete.")
        
        logging.info("Restarting service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_code = stdout.channel.recv_exit_status()
        if exit_code == 0:
            logging.info("Service restarted successfully.")
        else:
            logging.error(f"Service restart failed: {stderr.read().decode()}")

        sftp.close()
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
