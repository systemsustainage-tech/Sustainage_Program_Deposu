
import paramiko
import os
import sys

def deploy_debug_login():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage/tools'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'debug_login.py'))
        remote_path = f"{remote_dir}/debug_login.py"
        
        # Modify debug_login.py on the fly to check __super__
        with open(local_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace("check_login('admin', 'admin123')", "check_login('__super__', 'Kayra_1507')")
        content = content.replace("backend/data/sdg_desktop.sqlite", "/var/www/sustainage/backend/data/sdg_desktop.sqlite")
        # Fix imports for remote structure
        content = content.replace("from backend.yonetim.security.core.crypto", "sys.path.append('/var/www/sustainage')\nfrom yonetim.security.core.crypto")
        
        # Create a temp file
        temp_path = local_path.replace('.py', '_remote.py')
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Uploading debug script to {remote_path}...")
        sftp.put(temp_path, remote_path)
        os.remove(temp_path)
        
        print("Running debug script on remote...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_debug_login()
