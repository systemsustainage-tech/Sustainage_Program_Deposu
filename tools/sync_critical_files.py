import paramiko
import os
import logging
import time
import sys

# Configuration
HOST = '72.62.150.207'
PORT = 22
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_BASE = r'c:\SDG\server'
REMOTE_BASE = '/var/www/sustainage'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def upload_file(sftp, local_path, remote_path):
    try:
        sftp.put(local_path, remote_path)
        logging.info(f"Uploaded: {local_path} -> {remote_path}")
    except Exception as e:
        logging.error(f"Failed to upload {local_path}: {e}")

def upload_dir(sftp, local_dir, remote_dir):
    try:
        # Create remote dir if not exists
        try:
            sftp.stat(remote_dir)
        except IOError:
            sftp.mkdir(remote_dir)
            logging.info(f"Created remote dir: {remote_dir}")
            
        for item in os.listdir(local_dir):
            if item in ['.git', '__pycache__', 'venv', 'logs', 'node_modules']:
                continue
                
            local_path = os.path.join(local_dir, item)
            remote_path = remote_dir + '/' + item # Linux separator
            
            if os.path.isfile(local_path):
                upload_file(sftp, local_path, remote_path)
            elif os.path.isdir(local_path):
                upload_dir(sftp, local_path, remote_path)
                
    except Exception as e:
        logging.error(f"Failed to upload directory {local_dir}: {e}")

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        sftp = client.open_sftp()
        
        # Stop service first to release file locks
        logging.info("Stopping sustainage service...")
        client.exec_command("systemctl stop sustainage")
        time.sleep(2)

        # 1. Upload web_app.py
        logging.info("Uploading web_app.py...")
        upload_file(sftp, os.path.join(LOCAL_BASE, 'web_app.py'), REMOTE_BASE + '/web_app.py')
        
        # 2. Upload directories
        dirs_to_sync = ['templates', 'static', 'backend', 'utils', 'services']
        
        for d in dirs_to_sync:
            local_d = os.path.join(LOCAL_BASE, d)
            remote_d = REMOTE_BASE + '/' + d
            
            if os.path.exists(local_d):
                logging.info(f"Uploading directory: {d}...")
                upload_dir(sftp, local_d, remote_d)
            else:
                logging.warning(f"Local directory not found: {local_d}")

        # 3. Upload modules/gri/gri_gui.py specifically if needed? 
        # No, it should be in backend/modules/gri/gri_gui.py if structure matches.
        
        # 4. Set permissions
        logging.info("Setting permissions...")
        client.exec_command(f"chown -R www-data:www-data {REMOTE_BASE}")
        client.exec_command(f"find {REMOTE_BASE} -type d -exec chmod 755 {{}} +")
        client.exec_command(f"find {REMOTE_BASE} -type f -exec chmod 644 {{}} +")
        # Make web_app.py executable? Usually not needed for WSGI/Gunicorn but harmless
        # client.exec_command(f"chmod +x {REMOTE_BASE}/web_app.py")

        # 5. Restart service
        logging.info("Restarting sustainage service...")
        client.exec_command("systemctl start sustainage")
        
        # 6. Check status
        time.sleep(3)
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        status_out = stdout.read().decode()
        logging.info(f"Service Status:\n{status_out}")
        
        client.close()
        logging.info("Sync complete.")

    except Exception as e:
        logging.error(f"Sync failed: {e}")
        # Try to restart service anyway if it failed during upload
        try:
            client.exec_command("systemctl start sustainage")
        except:
            pass

if __name__ == "__main__":
    main()
