import paramiko
import os

def deploy_sdg_update():
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
        
        # 1. Upload update script
        local_script = os.path.join(os.getcwd(), 'tools/update_sdg_remote.py')
        remote_script = f"{remote_dir}/tools/update_sdg_remote.py"
        print(f"Uploading script to {remote_script}...")
        sftp.put(local_script, remote_script)
        
        # 2. Upload JSON data
        local_json = os.path.join(os.getcwd(), 'backend/data/sdg_data_dump.json')
        remote_json = f"{remote_dir}/backend/data/sdg_data_dump.json"
        print(f"Uploading JSON to {remote_json}...")
        sftp.put(local_json, remote_json)

        # 3. Upload updated sdg_manager.py
        local_manager = os.path.join(os.getcwd(), 'backend/modules/sdg/sdg_manager.py')
        remote_manager = f"{remote_dir}/backend/modules/sdg/sdg_manager.py"
        print(f"Uploading sdg_manager.py to {remote_manager}...")
        sftp.put(local_manager, remote_manager)
        
        # 4. Run update script
        print("Running update script...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_script}")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print("--- Output ---")
        print(out)
        print("--- Error ---")
        print(err)
        
        # 5. Restart Services
        print("Restarting services...")
        client.exec_command("systemctl restart sustainage")
        client.exec_command("systemctl restart nginx")
        print("Services restarted.")

    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_sdg_update()
