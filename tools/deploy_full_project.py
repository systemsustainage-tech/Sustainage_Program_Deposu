
import paramiko
import os
import sys
import zipfile
import time

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b)'

BASE_DIR = "c:\\SUSTAINAGESERVER"
ZIP_NAME = "deploy_package.zip"
REMOTE_DIR = "/var/www/sustainage"

EXCLUDE_DIRS = {'.git', '.trae', '.vscode', '__pycache__', 'venv', 'node_modules', '.idea'}
EXCLUDE_EXTENSIONS = {'.pyc', '.log', '.zip', '.tar.gz', '.rar', '.tmp'}

def create_zip(zip_path):
    print(f"Creating zip file: {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if any(file.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                    continue
                if file == ZIP_NAME:
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, BASE_DIR)
                try:
                    zipf.write(file_path, arcname)
                except Exception as e:
                    print(f"Skipping {file}: {e}")
    print("Zip created.")

def deploy():
    zip_path = os.path.join(BASE_DIR, ZIP_NAME)
    
    try:
        # 1. Create Zip
        create_zip(zip_path)
        
        # 2. Connect
        print(f"Connecting to {HOSTNAME}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # 3. Ensure remote directory exists
        print(f"Ensuring {REMOTE_DIR} exists...")
        client.exec_command(f"mkdir -p {REMOTE_DIR}")
        
        # 4. Upload Zip
        remote_zip = f"{REMOTE_DIR}/{ZIP_NAME}"
        print(f"Uploading {ZIP_NAME} to {remote_zip}...")
        sftp.put(zip_path, remote_zip)
        print("Upload complete.")
        
        # 5. Unzip Remotely (using Python to ensure compatibility)
        print("Extracting files...")
        unzip_cmd = (
            f"cd {REMOTE_DIR} && "
            f"python3 -c \"import zipfile; "
            f"print('Extracting...'); "
            f"zipfile.ZipFile('{ZIP_NAME}', 'r').extractall('.'); "
            f"print('Done.')\""
        )
        stdin, stdout, stderr = client.exec_command(unzip_cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            print(f"Unzip output: {out}")
            print(f"Unzip errors: {err}")
        else:
            print("Extraction successful.")
            
        # 6. Cleanup Zip
        client.exec_command(f"rm {remote_zip}")
        
        # 7. Install dependencies (optional but good)
        # print("Installing dependencies...")
        # client.exec_command(f"pip3 install -r {REMOTE_DIR}/requirements.txt")
        
        # 8. Restart Service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        client.close()
        print("Deployment complete!")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        # Cleanup local zip
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except:
                pass

if __name__ == '__main__':
    deploy()
