import paramiko
import os
import time

def deploy_webapp():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Upload web_app.py
        local_path = os.path.join(os.getcwd(), 'web_app.py')
        remote_path = f"{remote_dir}/web_app.py"
        print(f"Uploading web_app.py to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        print("Restarting services...")
        commands = [
            "systemctl restart sustainage",
            "systemctl restart nginx"
        ]
        for cmd in commands:
            print(f"Running: {cmd}")
            client.exec_command(cmd)
            time.sleep(1)
            
        print("Deployment complete.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_webapp()
