
import paramiko
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

REMOTE_SCRIPT = """
import os
import sys
import sqlite3
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def check_imports():
    logging.info("Checking imports...")
    try:
        import flask
        import argon2
        import pandas
        import matplotlib
        logging.info("Imports OK: flask, argon2, pandas, matplotlib")
    except ImportError as e:
        logging.error(f"Import Failed: {e}")
        return False
    return True

def check_db_user():
    logging.info("Checking DB User...")
    try:
        conn = sqlite3.connect('/var/www/sustainage/backend/data/sdg_desktop.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE username='__super__'")
        row = cursor.fetchone()
        if not row:
            logging.error("User __super__ not found!")
            return False
        
        phash = row[0]
        if phash == 'placeholder':
            logging.error("User has placeholder password!")
            return False
            
        # Verify password
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        try:
            ph.verify(phash, "super123")
            logging.info("Password verification: SUCCESS")
        except Exception as e:
            logging.error(f"Password verification FAILED: {e}")
            return False
            
        return True
    except Exception as e:
        logging.error(f"DB Check Failed: {e}")
        return False

def test_local_request():
    # Since the server might not be running or accessible from outside easily (if firewall/port issues),
    # we can try to run the app in a thread or just test the logic?
    # Actually, we can just assume if imports and DB are good, the CGI should work.
    # But checking if the CGI returns headers is good.
    # We can try running web_app.py as a script and check output.
    pass

if __name__ == "__main__":
    if check_imports() and check_db_user():
        logging.info("System is ready for login.")
    else:
        logging.error("System NOT ready.")
"""

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        sftp = client.open_sftp()
        with sftp.file('/var/www/sustainage/test_setup.py', 'w') as f:
            f.write(REMOTE_SCRIPT)
            
        logging.info("Running test script...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/test_setup.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
