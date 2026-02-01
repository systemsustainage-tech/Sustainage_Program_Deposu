
import paramiko
import os
import json
import sys

def validate_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data:
                print(f"Error: {file_path} is empty!")
                return False
            return True
    except Exception as e:
        print(f"Error validating {file_path}: {e}")
        return False

def deploy_translations():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_base = '/var/www/sustainage'
    
    print(f"Connecting to {hostname}...")
    
    # Files to deploy (local_rel_path, remote_rel_path)
    # We map both root locales and backend locales to ensure consistency
    files_map = [
        ('locales/tr.json', 'locales/tr.json'),
        ('locales/en.json', 'locales/en.json'),
        ('backend/locales/tr.json', 'backend/locales/tr.json'),
        ('backend/locales/en.json', 'backend/locales/en.json')
    ]
    
    # Validate local files first
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    valid_files = []
    
    for local_rel, remote_rel in files_map:
        local_path = os.path.join(base_dir, local_rel)
        if os.path.exists(local_path):
            if validate_json(local_path):
                valid_files.append((local_path, f"{remote_base}/{remote_rel}"))
            else:
                print(f"Skipping invalid file: {local_rel}")
                sys.exit(1) # Fail fast
        else:
            print(f"Warning: Local file not found: {local_rel}")

    if not valid_files:
        print("No valid files to deploy.")
        return

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        for local_path, remote_path in valid_files:
            print(f"Uploading {os.path.basename(local_path)} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
            except IOError as e:
                # Try to create directory if it fails?
                print(f"Upload failed (maybe dir missing?): {e}")
            
        print("Uploads complete. Restarting service to load new translations...")
        client.exec_command('systemctl restart sustainage')
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_translations()
