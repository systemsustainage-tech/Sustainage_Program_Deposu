import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_BASE = r'c:\SUSTAINAGESERVER'
REMOTE_BASE = '/var/www/sustainage'

FILES_TO_UPLOAD = [
    (r'backend\core\role_manager.py', 'backend/core/role_manager.py'),
    (r'backend\core\module_access.py', 'backend/core/module_access.py'),
    (r'backend\core\__init__.py', 'backend/core/__init__.py') # Just in case
]

def deploy_missing():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # Ensure remote directory exists
        remote_dir = f"{REMOTE_BASE}/backend/core"
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            print(f"Creating remote directory: {remote_dir}")
            client.exec_command(f"mkdir -p {remote_dir}")
        
        for local_rel, remote_rel in FILES_TO_UPLOAD:
            local_path = os.path.join(LOCAL_BASE, local_rel)
            remote_path = f"{REMOTE_BASE}/{remote_rel}"
            
            if os.path.exists(local_path):
                print(f"Uploading {local_path} to {remote_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"Warning: Local file not found: {local_path}")
        
        sftp.close()
        
        # Restart service
        print("Restarting service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # Check status
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        status = stdout.read().decode()
        print(status)
        
        if "active (running)" in status:
             print("SUCCESS: Service is running.")
        else:
             print("WARNING: Service might not be running.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_missing()
