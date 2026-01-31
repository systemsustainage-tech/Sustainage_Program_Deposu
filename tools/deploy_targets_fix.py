import paramiko
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'

files_to_deploy = [
    # Fixed TargetManager with robust error handling and DB path support
    (r'c:\SUSTAINAGESERVER\backend\modules\reporting\target_manager.py', '/var/www/sustainage/backend/modules/reporting/target_manager.py'),
    # Fixed config/database.py with Linux path support
    (r'c:\SUSTAINAGESERVER\config\database.py', '/var/www/sustainage/config/database.py'),
    # Updated web_app.py passing DB_PATH
    (r'c:\SUSTAINAGESERVER\web_app.py', '/var/www/sustainage/web_app.py'),
    # Ensure template is present
    (r'c:\SUSTAINAGESERVER\templates\targets.html', '/var/www/sustainage/templates/targets.html')
]

def deploy():
    print(f"Connecting to {HOSTNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()
        
        for local, remote in files_to_deploy:
            if os.path.exists(local):
                print(f"Deploying {local} -> {remote}")
                # Ensure remote directory exists
                remote_dir = os.path.dirname(remote)
                try:
                    sftp.stat(remote_dir)
                except FileNotFoundError:
                    print(f"Creating remote directory: {remote_dir}")
                    ssh.exec_command(f"mkdir -p {remote_dir}")
                    time.sleep(1)
                
                sftp.put(local, remote)
            else:
                print(f"Local file not found: {local}")
        
        print("Restarting Gunicorn...")
        ssh.exec_command("systemctl restart sustainage_app")
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy()
