import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_BASE = r'c:\SUSTAINAGESERVER'
REMOTE_BASE = '/var/www/sustainage'

FILES_TO_UPLOAD = [
    ('web_app.py', 'web_app.py'),
    (r'backend\app\api\role_api.py', 'backend/app/api/role_api.py'),
    (r'backend\app\api\__init__.py', 'backend/app/api/__init__.py') # Assuming it might be needed, though not strictly required if implicit namespace, but good practice.
]

def deploy_fix():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # Ensure remote directory exists
        remote_dir = f"{REMOTE_BASE}/backend/app/api"
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            print(f"Creating remote directory: {remote_dir}")
            # Recursively create? No, backend/app should exist.
            try:
                sftp.mkdir(remote_dir)
            except IOError:
                # Maybe parent missing?
                client.exec_command(f"mkdir -p {remote_dir}")
        
        for local_rel, remote_rel in FILES_TO_UPLOAD:
            local_path = os.path.join(LOCAL_BASE, local_rel)
            remote_path = f"{REMOTE_BASE}/{remote_rel}"
            
            if os.path.exists(local_path):
                print(f"Uploading {local_path} to {remote_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"Warning: Local file not found: {local_path}")
                # Check if we can create __init__.py on the fly if it's missing locally
                if 'check_init' in local_rel or '__init__' in local_rel:
                     # If local __init__.py missing, maybe create empty one on remote?
                     pass
        
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
    deploy_fix()
