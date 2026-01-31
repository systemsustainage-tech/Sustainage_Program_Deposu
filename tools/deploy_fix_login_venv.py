import paramiko
import os
import sys

def deploy_fix_login_venv():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage'
    venv_python = '/var/www/sustainage/venv/bin/python'

    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Files to upload
        files_to_upload = [
            ('tools/fix_remote_super_user.py', 'tools/fix_remote_super_user.py')
        ]
        
        for local, remote in files_to_upload:
            local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', local))
            remote_path = f"{remote_dir}/{remote}"
            
            print(f"Uploading {local} to {remote_path}...")
            sftp.put(local_path, remote_path)
            
        print("Uploads complete.")
        
        # Run script with VENV python
        script = 'tools/fix_remote_super_user.py'
        print(f"Running {script} on remote with {venv_python}...")
        stdin, stdout, stderr = client.exec_command(f"{venv_python} {remote_dir}/{script}")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out: print(f"Output:\n{out}")
        if err: print(f"Error:\n{err}")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_fix_login_venv()
