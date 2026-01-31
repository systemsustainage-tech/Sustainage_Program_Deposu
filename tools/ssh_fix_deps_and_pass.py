
import paramiko
import logging
import time

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
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def install_package(pkg):
    try:
        logging.info(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--break-system-packages", "--ignore-installed"])
        logging.info(f"Installed {pkg}")
    except Exception as e:
        logging.error(f"Failed to install {pkg}: {e}")

def fix_dependencies():
    # Install critical packages individually to avoid batch failure
    pkgs = ["argon2-cffi", "flask", "flask-session", "werkzeug", "pandas", "openpyxl", "requests", "matplotlib"]
    for pkg in pkgs:
        install_package(pkg)

def update_password():
    logging.info("Updating Super User Password...")
    try:
        from argon2 import PasswordHasher
        ph = PasswordHasher()
        password_hash = ph.hash("super123")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash=? WHERE username='__super__'", (password_hash,))
        conn.commit()
        conn.close()
        logging.info("Password updated successfully.")
        
    except ImportError:
        logging.error("CRITICAL: argon2-cffi still not found!")
    except Exception as e:
        logging.error(f"Password update failed: {e}")

def main():
    fix_dependencies()
    update_password()
    # Final permission fix
    subprocess.call(["chown", "-R", "www-data:www-data", "/var/www/sustainage"])

if __name__ == "__main__":
    main()
"""

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        sftp = client.open_sftp()
        with sftp.file('/var/www/sustainage/fix_deps.py', 'w') as f:
            f.write(REMOTE_SCRIPT)
        
        logging.info("Running fix script...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/fix_deps.py")
        
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.strip())
            
        err = stderr.read().decode()
        if err:
            logging.error(f"Errors:\n{err}")
            
        client.exec_command("rm /var/www/sustainage/fix_deps.py")
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
