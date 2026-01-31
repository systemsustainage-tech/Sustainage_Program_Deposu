
import paramiko
import logging
import os
import sys
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Credentials
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

REMOTE_BASE = '/var/www/sustainage'
LOCAL_BASE = os.getcwd()

FILES_TO_DEPLOY = [
    'backend/modules/esrs/esrs_manager.py',
    'web_app.py',
    'remote_web_app.py',
    'templates/esrs.html'
]

def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        logging.info("Connected to SSH")
        
        sftp = ssh.open_sftp()
        
        for file_path in FILES_TO_DEPLOY:
            local_path = os.path.join(LOCAL_BASE, file_path)
            remote_path = f"{REMOTE_BASE}/{file_path}"
            
            try:
                # Ensure remote dir exists
                remote_dir = os.path.dirname(remote_path)
                try:
                    sftp.stat(remote_dir)
                except IOError:
                    logging.info(f"Creating remote directory: {remote_dir}")
                    # Simple mkdir, might fail if parent missing, but usually structure exists
                    sftp.mkdir(remote_dir)
                
                sftp.put(local_path, remote_path)
                logging.info(f"Uploaded: {file_path}")
            except Exception as e:
                logging.error(f"Failed to upload {file_path}: {e}")

        sftp.close()
        
        # Restart service
        logging.info("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage')
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            logging.info("Service restarted successfully.")
        else:
            logging.error(f"Service restart failed: {stderr.read().decode()}")

        ssh.close()
        logging.info("Deployment cycle complete.")
        
    except Exception as e:
        logging.error(f"Deployment failed: {e}")

if __name__ == '__main__':
    deploy()
