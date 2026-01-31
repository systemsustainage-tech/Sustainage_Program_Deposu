
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

def check_remote_file(sftp, path):
    try:
        sftp.stat(path)
        logging.info(f"[OK] Found: {path}")
        return True
    except IOError:
        logging.error(f"[MISSING] Not found: {path}")
        return False

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        sftp = client.open_sftp()
        logging.info("Connected.")
        
        # Check critical files
        files_to_check = [
            f"{REMOTE_BASE}/web_app.py",
            f"{REMOTE_BASE}/backend/__init__.py",
            f"{REMOTE_BASE}/backend/modules/__init__.py",
            f"{REMOTE_BASE}/backend/modules/security/__init__.py",
            f"{REMOTE_BASE}/backend/modules/security/rate_limiter.py",
            f"{REMOTE_BASE}/backend/modules/security/hardware_lock.py",
            f"{REMOTE_BASE}/yonetim/kullanici_yonetimi/models/user_manager.py",
            f"{REMOTE_BASE}/yonetim/__init__.py",
            f"{REMOTE_BASE}/yonetim/security/core/crypto.py"
        ]
        
        logging.info("--- Verifying Critical Files ---")
        for f in files_to_check:
            check_remote_file(sftp, f)
            
        # Check if yonetim exists in backend just in case
        check_remote_file(sftp, f"{REMOTE_BASE}/backend/yonetim")

        sftp.close()
        client.close()

    except Exception as e:
        logging.error(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
