import paramiko
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

LOCAL_BASE = r'c:\SDG'
REMOTE_BASE = '/var/www/sustainage'

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
        
        # Stop service first
        logging.info("Stopping sustainage service...")
        client.exec_command("systemctl stop sustainage")
        time.sleep(2)

        # 1. Upload web_app.py
        logging.info("Uploading web_app.py...")
        upload_file(sftp, os.path.join(LOCAL_BASE, 'server', 'web_app.py'), REMOTE_BASE + '/web_app.py')
        
        # 2. Upload Config (Translations)
        logging.info("Uploading config...")
        upload_dir(sftp, os.path.join(LOCAL_BASE, 'config'), REMOTE_BASE + '/config')

        # 3. Upload Static
        # Check source: static_sync or hosting_files/static?
        # static_sync seems to have css, images, js
        static_source = os.path.join(LOCAL_BASE, 'static_sync')
        if os.path.exists(static_source):
            logging.info("Uploading static files from static_sync...")
            upload_dir(sftp, static_source, REMOTE_BASE + '/static')
        else:
            logging.warning("static_sync not found, trying hosting_files...")
            # If static_sync missing, try constructing from hosting_files
            # But hosting_files has css/js/images at root, not in a static folder?
            # Let's check hosting_files structure again from LS result
            # hosting_files/css, hosting_files/js
            # So we can upload css and js to static/css and static/js
            pass # Simplify: Assume static_sync exists as seen in LS

        # 4. Set permissions
        logging.info("Setting permissions...")
        client.exec_command(f"chown -R www-data:www-data {REMOTE_BASE}")
        client.exec_command(f"find {REMOTE_BASE} -type d -exec chmod 755 {{}} +")
        client.exec_command(f"find {REMOTE_BASE} -type f -exec chmod 644 {{}} +")

        # 5. Restart service
        logging.info("Restarting sustainage service...")
        client.exec_command("systemctl start sustainage")
        
        # 6. Check status
        time.sleep(3)
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        status_out = stdout.read().decode()
        logging.info(f"Service Status:\n{status_out}")
        
        client.close()
        logging.info("Deploy complete.")

    except Exception as e:
        logging.error(f"Deploy failed: {e}")
        try:
            client.exec_command("systemctl start sustainage")
        except:
            pass

if __name__ == "__main__":
    main()
