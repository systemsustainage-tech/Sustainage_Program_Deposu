import paramiko
import os

def deploy_mapping_fix():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_path = '/var/www/sustainage/mapping/__init__.py'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        print(f"Creating {remote_path}...")
        with sftp.open(remote_path, 'w') as f:
            f.write("")
            
        print("Restarting service...")
        client.exec_command("systemctl restart sustainage")
        print("Done.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_mapping_fix()
