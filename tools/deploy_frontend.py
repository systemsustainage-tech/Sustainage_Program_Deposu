import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_ROOT = 'c:\\SUSTAINAGESERVER'
REMOTE_ROOT = '/var/www/sustainage'

FOLDERS_TO_SYNC = ['frontend']
FILES_TO_SYNC = ['web_app.py']

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = client.open_sftp()
        
        # Sync Files
        for filename in FILES_TO_SYNC:
            local_path = os.path.join(LOCAL_ROOT, filename)
            remote_path = f"{REMOTE_ROOT}/{filename}"
            print(f"Uploading {local_path} -> {remote_path}")
            sftp.put(local_path, remote_path)
            
        # Sync Folders
        for folder in FOLDERS_TO_SYNC:
            local_folder = os.path.join(LOCAL_ROOT, folder)
            remote_folder = f"{REMOTE_ROOT}/{folder}"
            
            # Ensure remote folder exists
            try:
                sftp.stat(remote_folder)
            except FileNotFoundError:
                print(f"Creating remote directory: {remote_folder}")
                sftp.mkdir(remote_folder)
                
            for root, dirs, files in os.walk(local_folder):
                rel_path = os.path.relpath(root, local_folder)
                if rel_path == '.':
                    remote_path = remote_folder
                else:
                    remote_path = f"{remote_folder}/{rel_path.replace(os.sep, '/')}"
                
                # Create remote directories
                for d in dirs:
                    remote_dir = f"{remote_path}/{d}"
                    try:
                        sftp.stat(remote_dir)
                    except FileNotFoundError:
                        print(f"Creating remote directory: {remote_dir}")
                        sftp.mkdir(remote_dir)
                
                for file in files:
                    local_file = os.path.join(root, file)
                    remote_file = f"{remote_path}/{file}"
                    # print(f"Uploading {local_file} -> {remote_file}")
                    try:
                        sftp.put(local_file, remote_file)
                    except Exception as e:
                        print(f"Failed to upload {file}: {e}")

        sftp.close()
        
        print("Restarting services...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        client.close()
        print("Deployment complete.")
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
