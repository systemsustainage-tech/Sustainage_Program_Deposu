import paramiko
import os
import sys

def deploy_webapp_fix():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage'
    
    # We deploy local 'remote_web_app.py' to remote 'web_app.py' because that's what wsgi imports
    files_to_upload = [
        ('remote_web_app.py', 'web_app.py'),
    ]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        for local_path, remote_rel_path in files_to_upload:
            local_full = os.path.join(os.getcwd(), local_path)
            remote_full = f"{remote_dir}/{remote_rel_path}"
            
            if os.path.exists(local_full):
                print(f"Uploading {local_path} -> {remote_full}...")
                sftp.put(local_full, remote_full)
            else:
                print(f"Error: Local file {local_path} not found!")
                return
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Stderr: {err}")
        
        print("Done.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_webapp_fix()
