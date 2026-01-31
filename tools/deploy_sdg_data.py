import paramiko
import os
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

files_to_deploy = [
    ('c:/SUSTAINAGESERVER/backend/data/sdg_data_dump.json', 'backend/data/sdg_data_dump.json'),
    ('c:/SUSTAINAGESERVER/tools/import_sdg_data.py', 'tools/import_sdg_data.py'),
]

def deploy_and_import():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        for local_path, remote_rel_path in files_to_deploy:
            if not os.path.exists(local_path):
                print(f"Local file not found: {local_path}")
                continue
                
            remote_path = f"{remote_base}/{remote_rel_path}"
            # Ensure directory exists
            remote_dir = os.path.dirname(remote_path)
            try:
                sftp.stat(remote_dir)
            except IOError:
                # Create directory if it doesn't exist (recursively might be needed but assuming parent dirs exist for now)
                # Simple check, assuming backend/data exists
                pass

            print(f"Uploading {local_path} to {remote_path}...")
            sftp.put(local_path, remote_path)
            print("Success.")
                
        sftp.close()

        print("Running import_sdg_data.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/import_sdg_data.py")
        print("--- Output ---")
        print(stdout.read().decode())
        print("--- Errors ---")
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_and_import()
