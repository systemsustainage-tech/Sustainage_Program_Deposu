import paramiko
import os

def deploy_missing_modules():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_base = '/var/www/sustainage/backend/modules/environmental'
    
    files_to_deploy = [
        'water_reporting.py',
        '__init__.py'
    ]
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Ensure remote directory exists
        try:
            sftp.stat(remote_base)
        except FileNotFoundError:
            print(f"Creating remote directory: {remote_base}")
            sftp.mkdir(remote_base)
            
        for fname in files_to_deploy:
            local_path = os.path.join('backend', 'modules', 'environmental', fname)
            remote_path = f"{remote_base}/{fname}"
            
            if os.path.exists(local_path):
                print(f"Uploading {local_path} -> {remote_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"Warning: Local file {local_path} not found!")

        print("Restarting service...")
        client.exec_command("systemctl restart sustainage")
        print("Done.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_missing_modules()
