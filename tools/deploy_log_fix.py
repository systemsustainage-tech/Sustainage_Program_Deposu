import paramiko
import os
import sys

# Remote server details
hostname = '72.62.150.207'
username = 'root'
password = os.environ.get('REMOTE_PASS', 'Sustainage123.')

def deploy_log_fix():
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Files to upload
        files_to_upload = [
            (r'c:\SUSTAINAGESERVER\backend\core\db_log_handler.py', '/var/www/sustainage/backend/core/db_log_handler.py'),
            (r'c:\SUSTAINAGESERVER\web_app.py', '/var/www/sustainage/web_app.py')
        ]
        
        for local, remote in files_to_upload:
            print(f"Uploading {local} to {remote}...")
            sftp.put(local, remote)
            
        sftp.close()
        
        # Restart service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command('systemctl restart sustainage')
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out: print(f"Output: {out}")
        if err: print(f"Error: {err}")
        
        print("Service restarted.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_log_fix()
