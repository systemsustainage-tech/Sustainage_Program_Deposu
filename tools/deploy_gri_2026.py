import paramiko
import os
import sys

def deploy_gri_2026():
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
            ('backend/modules/gri/gri_manager.py', 'backend/modules/gri/gri_manager.py'),
            ('templates/gri.html', 'templates/gri.html'),
            ('locales/tr.json', 'locales/tr.json'),
            ('locales/en.json', 'locales/en.json'),
            ('backend/data/gri_2026_update.json', 'backend/data/gri_2026_update.json'),
            ('tools/update_gri_data_2026.py', 'tools/update_gri_data_2026.py'),
            ('tools/fix_gri_sectors.py', 'tools/fix_gri_sectors.py')
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
            
        print("Uploads complete.")
        
        # Run update scripts on remote
        scripts_to_run = [
            'tools/update_gri_data_2026.py',
            'tools/fix_gri_sectors.py'
        ]
        
        for script in scripts_to_run:
            print(f"Running {script} on remote...")
            stdin, stdout, stderr = client.exec_command(f"python3 {remote_dir}/{script}")
            
            # Print output in real-time or after
            out = stdout.read().decode()
            err = stderr.read().decode()
            if out: print(f"[{script}] Output:\n{out}")
            if err: print(f"[{script}] Error:\n{err}")

        # Restart service (optional check)
        # We can touch web_app.py to trigger reload if using uwsgi/gunicorn with auto-reload
        # client.exec_command(f"touch {remote_dir}/web_app.py")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_gri_2026()
