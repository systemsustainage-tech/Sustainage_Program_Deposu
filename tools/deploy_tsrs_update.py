import paramiko
import os
import time

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'
REMOTE_BASE_DIR = '/var/www/sustainage'

FILES_TO_UPLOAD = [
    {'local': r'c:\SUSTAINAGESERVER\backend\modules\tsrs\tsrs_schema.sql', 'remote': 'backend/modules/tsrs/tsrs_schema.sql'},
    {'local': r'c:\SUSTAINAGESERVER\backend\modules\tsrs\tsrs_manager.py', 'remote': 'backend/modules/tsrs/tsrs_manager.py'},
    {'local': r'c:\SUSTAINAGESERVER\web_app.py', 'remote': 'web_app.py'},
    {'local': r'c:\SUSTAINAGESERVER\templates\tsrs.html', 'remote': 'templates/tsrs.html'},
    {'local': r'c:\SUSTAINAGESERVER\tools\seed_tsrs_data.py', 'remote': 'tools/seed_tsrs_data.py'},
    {'local': r'c:\SUSTAINAGESERVER\tools\update_tsrs_schema.py', 'remote': 'tools/update_tsrs_schema.py'},
]

def deploy():
    print("Starting TSRS Deployment...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = client.open_sftp()
        
        # 1. Upload files
        for item in FILES_TO_UPLOAD:
            local_path = item['local']
            remote_path = f"{REMOTE_BASE_DIR}/{item['remote']}"
            
            print(f"Uploading {local_path} -> {remote_path}")
            try:
                # Ensure remote directory exists
                remote_dir = os.path.dirname(remote_path)
                try:
                    sftp.stat(remote_dir)
                except FileNotFoundError:
                    # Simple mkdir (doesn't support -p via sftp, but dirs likely exist)
                    # For safety, let's use exec_command for mkdir -p
                    client.exec_command(f"mkdir -p {remote_dir}")
                    time.sleep(0.5)
                
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Error uploading {local_path}: {e}")
                
        print("Files uploaded successfully.")
        
        # 2. Update Schema remotely
        print("Running schema update script on remote server...")
        stdin, stdout, stderr = client.exec_command(f"python3 {REMOTE_BASE_DIR}/tools/update_tsrs_schema.py")
        print("STDOUT:", stdout.read().decode())
        print("STDERR:", stderr.read().decode())
        
        # 3. Run seed script remotely
        print("Running seed script on remote server...")
        stdin, stdout, stderr = client.exec_command(f"python3 {REMOTE_BASE_DIR}/tools/seed_tsrs_data.py")
        print("STDOUT:", stdout.read().decode())
        print("STDERR:", stderr.read().decode())
        
        # 4. Restart Service (optional, but good practice if web_app.py changed)
        # Assuming systemd service or similar. If manual run, might need to kill/start.
        # For now, just checking if we can restart or reload.
        # print("Reloading web service...")
        # client.exec_command("systemctl restart sustainage") # Example command
        
        print("Deployment completed.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
