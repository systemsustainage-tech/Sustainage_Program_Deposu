
import paramiko
import os
import sys
import time

def deploy_gri_fix():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage'
    
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Files to upload
        files_to_upload = [
            ('remote_web_app.py', 'web_app.py'),
            ('templates/gri.html', 'templates/gri.html')
        ]
        
        for local, remote in files_to_upload:
            local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', local))
            remote_path = f"{remote_dir}/{remote}"
            
            if not os.path.exists(local_path):
                print(f"Error: Local file not found: {local_path}")
                continue
                
            print(f"Uploading {local} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Failed to upload {local}: {e}")
        
        print("Uploads complete. Restarting service...")
        
        # Restart service
        stdin, stdout, stderr = client.exec_command('systemctl restart sustainage')
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")
            
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_gri_fix()
