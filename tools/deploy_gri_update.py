import paramiko
import os

def deploy_gri_update():
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
        
        # Files to upload
        files_to_upload = [
            ('web_app.py', 'web_app.py'),
            ('locales/tr.json', 'locales/tr.json'),
            ('locales/en.json', 'locales/en.json'),
            ('tools/update_gri_2025.py', 'tools/update_gri_2025.py')
        ]
        
        for local, remote in files_to_upload:
            local_path = os.path.join(os.getcwd(), local)
            remote_path = f"{remote_dir}/{remote}"
            print(f"Uploading {local} to {remote_path}...")
            sftp.put(local_path, remote_path)
            
        print("Uploads complete.")
        
        # Run update_gri_2025.py on remote
        print("Running update_gri_2025.py on remote...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_dir}/tools/update_gri_2025.py")
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out: print(f"Output: {out}")
        if err: print(f"Error: {err}")
        
        # Restart service (optional, but good practice if web_app.py changed)
        # Assuming gunicorn or systemd service, but usually we just update files.
        # If running via python web_app.py manually, might need restart.
        # For now, just updating files.
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_gri_update()
