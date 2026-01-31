import paramiko
import logging
import sys
import os

# Configuration
HOST = '72.62.150.207'
PORT = 22
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
LOCAL_CSS_DIR = 'c:/SDG/hosting_files/css'
REMOTE_STATIC_DIR = '/var/www/sustainage/static'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        sftp = client.open_sftp()

        # Create static directory if not exists
        try:
            sftp.stat(REMOTE_STATIC_DIR)
        except FileNotFoundError:
            logging.info(f"Creating {REMOTE_STATIC_DIR}...")
            sftp.mkdir(REMOTE_STATIC_DIR)

        # Create css directory
        remote_css_dir = f"{REMOTE_STATIC_DIR}/css"
        try:
            sftp.stat(remote_css_dir)
        except FileNotFoundError:
            logging.info(f"Creating {remote_css_dir}...")
            sftp.mkdir(remote_css_dir)

        # Upload files
        if os.path.exists(LOCAL_CSS_DIR):
            for file in os.listdir(LOCAL_CSS_DIR):
                local_path = os.path.join(LOCAL_CSS_DIR, file)
                remote_path = f"{remote_css_dir}/{file}"
                if os.path.isfile(local_path):
                    logging.info(f"Uploading {file}...")
                    sftp.put(local_path, remote_path)
        else:
            logging.warning(f"Local CSS dir not found: {LOCAL_CSS_DIR}")

        sftp.close()
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
