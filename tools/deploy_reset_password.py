import paramiko
import os
import sys

def deploy_and_reset():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage/tools'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'reset_super_password.py'))
        remote_path = f"{remote_dir}/reset_super_password.py"
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        print("Running reset script...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_and_reset()
