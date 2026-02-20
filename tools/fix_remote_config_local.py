import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
if not os.path.exists(KEY_FILE):
    KEY_FILE = os.path.expanduser("~/.ssh/id_ed25519")

config_content = """import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if os.name == 'nt':
    DB_PATH = os.path.join(BACKEND_DIR, "data", "sdg_desktop.sqlite")
else:
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def get_db_path():
    return DB_PATH
"""

def update_remote_config():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    try:
        sftp = ssh.open_sftp()
        print("Writing to /var/www/sustainage/config/database.py...")
        with sftp.file('/var/www/sustainage/config/database.py', 'w') as f:
            f.write(config_content)
        
        print("Updated /var/www/sustainage/config/database.py")
        sftp.close()
    except Exception as e:
        print(f"SFTP failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    update_remote_config()
