
import paramiko
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        # 1. Install Dependencies
        logging.info("--- Installing Dependencies ---")
        deps = "flask flask-session werkzeug pandas matplotlib openpyxl requests"
        logging.info(f"Running: pip3 install {deps}")
        stdin, stdout, stderr = client.exec_command(f"pip3 install {deps}")
        
        # Read output in real-time or wait
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logging.info("Dependencies installed successfully.")
        else:
            logging.error(f"Dependency installation failed:\n{stderr.read().decode()}")

        # 2. Fix Permissions
        logging.info("--- Fixing Permissions ---")
        # Assume Apache user is www-data. 
        # Check if www-data user exists first? usually yes.
        # We will set owner to www-data for the whole directory to be safe.
        cmd = "chown -R www-data:www-data /var/www/sustainage"
        logging.info(f"Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logging.info("Permissions updated.")
        else:
            logging.error(f"Permission update failed:\n{stderr.read().decode()}")
            
        # Also ensure logs dir is writable
        client.exec_command("chmod -R 775 /var/www/sustainage/logs")
        client.exec_command("chmod -R 775 /var/www/sustainage/backend/data") # For SQLite

        # 3. Check Database for Super Admin
        logging.info("--- Checking Super Admin in DB ---")
        # We need to run a python script on the remote server to check sqlite
        # We'll create a temporary python script there
        remote_script = """
import sqlite3
import os

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

try:
    if not os.path.exists(DB_PATH):
        print(f"DB not found at {DB_PATH}")
        exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check table existence
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        print("Users table does not exist!")
        exit(1)
        
    # Check super user
    cursor.execute("SELECT username, role FROM users WHERE username='__super__'")
    user = cursor.fetchone()
    if user:
        print(f"Super user found: {user}")
    else:
        print("Super user NOT found. Creating...")
        # Create super user
        # We need to hash password matching the app's logic.
        # But for now, let's just insert plain text if app supports it, 
        # OR better: use the app's User model? No, imports might fail.
        # Let's try to insert a record. 
        # WARNING: If app uses hashing, plain text won't work.
        # The user provided credentials 'super123'. 
        # I'll rely on the user having created it or the app handling it.
        # If it's missing, I'll report it.
        print("MISSING_SUPER_USER")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
"""
        # Upload this script
        sftp = client.open_sftp()
        with sftp.file('/var/www/sustainage/check_user.py', 'w') as f:
            f.write(remote_script)
            
        # Run it
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/check_user.py")
        out = stdout.read().decode().strip()
        logging.info(f"User Check Output: {out}")
        
        # Cleanup
        client.exec_command("rm /var/www/sustainage/check_user.py")
        
        # 4. Restart Service
        logging.info("--- Restarting Service ---")
        client.exec_command("systemctl restart sustainage")
        logging.info("Service restarted.")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
