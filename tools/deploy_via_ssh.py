
import paramiko
import logging
import os
import sys
from stat import S_ISDIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

REMOTE_BASE = '/var/www/sustainage'
LOCAL_SERVER_DIR = 'c:/SDG/server'
LOCAL_YONETIM_DIR = 'c:/SDG/yonetim'
LOCAL_TASKS_DIR = 'c:/SDG/tasks'
LOCAL_MODULES_DIR = 'c:/SDG/modules'

def put_dir_recursive(sftp, local_dir, remote_dir):
    """Recursively uploads a directory to the remote server."""
    # Create remote directory if it doesn't exist
    try:
        sftp.stat(remote_dir)
    except IOError:
        try:
            sftp.mkdir(remote_dir)
            logging.info(f"Created remote directory: {remote_dir}")
        except Exception as e:
             logging.error(f"Failed to create {remote_dir}: {e}")

    try:
        items = os.listdir(local_dir)
    except Exception as e:
        logging.error(f"Failed to list local directory {local_dir}: {e}")
        return

    for item in items:
        if item in ['.git', '__pycache__', '.env', 'venv', 'logs', '.DS_Store', 'sdg.db', 'sdg_desktop.sqlite', 'node_modules']:
            continue
            
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"

        if os.path.isdir(local_path):
            put_dir_recursive(sftp, local_path, remote_path)
        elif os.path.isfile(local_path):
            try:
                # Always overwrite for now to ensure consistency
                sftp.put(local_path, remote_path)
                logging.info(f"Uploaded: {item} -> {remote_path}")
                
                # Set permissions
                if item.endswith('.py') or item.endswith('.sh'):
                    try:
                        sftp.chmod(remote_path, 0o755)
                    except:
                        pass
                else:
                    try:
                        sftp.chmod(remote_path, 0o644)
                    except:
                        pass
            except Exception as e:
                logging.error(f"Failed to upload {local_path} to {remote_path}: {e}")

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        sftp = client.open_sftp()
        logging.info("Connected.")
        
        # 1. Upload Server Directory (Core App)
        logging.info("--- Deploying Server Files (includes backend) ---")
        put_dir_recursive(sftp, LOCAL_SERVER_DIR, REMOTE_BASE)
        
        # 2. Upload Yonetim Directory (Admin Tools)
        logging.info("--- Deploying Yonetim Files ---")
        put_dir_recursive(sftp, LOCAL_YONETIM_DIR, f"{REMOTE_BASE}/yonetim")
        
        # 3. Upload Tasks Directory
        logging.info("--- Deploying Tasks Files ---")
        put_dir_recursive(sftp, LOCAL_TASKS_DIR, f"{REMOTE_BASE}/tasks")
        
        # 4. Upload Modules Directory
        logging.info("--- Deploying Modules Files ---")
        put_dir_recursive(sftp, LOCAL_MODULES_DIR, f"{REMOTE_BASE}/modules")
        
        sftp.close()
        
        # 5. Restart Service
        logging.info("--- Restarting Service ---")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_code = stdout.channel.recv_exit_status()
        if exit_code == 0:
            logging.info("Service restarted successfully.")
        else:
            logging.error(f"Service restart failed: {stderr.read().decode()}")
            
    except Exception as e:
        logging.error(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
