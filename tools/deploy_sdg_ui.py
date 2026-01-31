
import paramiko
import os
import time

def deploy_sdg_ui():
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
        print("Connected.")

        # 1. Upload Templates
        files_to_upload = [
            ('templates/sdg.html', 'templates/sdg.html'),
            ('templates/sdg_edit.html', 'templates/sdg_edit.html'),
            ('remote_web_app.py', 'web_app.py'), # Upload as web_app.py
            ('tools/verify_sdg_remote_data.py', 'tools/verify_sdg_remote_data.py')
        ]

        for local_file, remote_file in files_to_upload:
            local_path = os.path.join(os.getcwd(), local_file)
            remote_path = f"{remote_dir}/{remote_file}"
            
            if os.path.exists(local_path):
                print(f"Uploading {local_file} to {remote_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"WARNING: Local file {local_file} not found!")

        # 2. Upload Mapping File (Ensure directory exists)
        mapping_dir = f"{remote_dir}/mapping"
        try:
            sftp.stat(mapping_dir)
        except IOError:
            print(f"Creating remote directory: {mapping_dir}")
            sftp.mkdir(mapping_dir)
        
        sftp.put(os.path.join(os.getcwd(), 'mapping/sdg_gri_mapping.py'), f"{mapping_dir}/sdg_gri_mapping.py")
        print("Uploaded mapping/sdg_gri_mapping.py")

        # 3. Verify Data
        print("Running verification script...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_dir}/tools/verify_sdg_remote_data.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Verification Errors: {err}")

        # 4. Restart Services
        print("Restarting services...")
        client.exec_command("systemctl restart sustainage")
        client.exec_command("systemctl restart nginx")
        print("Services restarted.")

    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_sdg_ui()
