import paramiko
import os
import sys

def deploy_sdg_fix():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage'
    
    # Files to upload
    files_to_deploy = [
        ('web_app.py', 'web_app.py'),
        ('backend/modules/sdg/sdg_manager.py', 'backend/modules/sdg/sdg_manager.py'),
        ('templates/sdg.html', 'templates/sdg.html')
    ]
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        for local_path, remote_rel_path in files_to_deploy:
            full_local_path = os.path.abspath(os.path.join(os.getcwd(), local_path))
            full_remote_path = f"{remote_dir}/{remote_rel_path}"
            
            print(f"Uploading {local_path} to {full_remote_path}...")
            try:
                sftp.put(full_local_path, full_remote_path)
            except Exception as e:
                print(f"Error uploading {local_path}: {e}")
                # Try to create directory if it doesn't exist (though it should)
                # ...
        
        # Restart Services
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Done.")

    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_sdg_fix()
