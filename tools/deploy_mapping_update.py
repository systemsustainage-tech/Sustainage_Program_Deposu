
import paramiko
import os

def deploy_mapping_update():
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
        
        # Upload script
        local_path = os.path.join(os.getcwd(), 'tools/update_sdg_mappings_remote.py')
        remote_path = f"{remote_dir}/update_sdg_mappings_remote.py"
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        # Run script
        print("Running update script...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Errors: {err}")
            
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_mapping_update()
