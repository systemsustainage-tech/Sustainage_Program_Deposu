import os
import sys
import paramiko

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.database import DB_PATH

def deploy_updates():
    hostname = "72.62.150.207"
    username = "root"
    key_path = os.path.expanduser("~/.ssh/id_rsa")
    
    remote_base = "/var/www/sustainage"
    
    files_to_deploy = [
        (r"c:\SUSTAINAGESERVER\backend\modules\file_manager\advanced_file_manager.py", 
         f"{remote_base}/backend/modules/file_manager/advanced_file_manager.py"),
        (r"c:\SUSTAINAGESERVER\locales\tr.json", 
         f"{remote_base}/locales/tr.json"),
        (r"c:\SUSTAINAGESERVER\remote_web_app.py", 
         f"{remote_base}/remote_web_app.py"),
        (r"c:\SUSTAINAGESERVER\tools\migrate_file_manager_isolation.py", 
         f"{remote_base}/tools/migrate_file_manager_isolation.py")
    ]
    
    print(f"Connecting to {hostname}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect using key if exists, else try agent/password (assuming agent is active)
        if os.path.exists(key_path):
            ssh.connect(hostname, username=username, key_filename=key_path)
        else:
            print(f"Key not found at {key_path}, trying default/agent...")
            ssh.connect(hostname, username=username)
        
        sftp = ssh.open_sftp()
        
        for local, remote in files_to_deploy:
            print(f"Uploading {local} -> {remote}")
            try:
                sftp.put(local, remote)
            except Exception as e:
                print(f"Failed to upload {local}: {e}")
                # Try to create directory if it fails
                remote_dir = os.path.dirname(remote)
                print(f"Ensuring directory exists: {remote_dir}")
                ssh.exec_command(f"mkdir -p {remote_dir}")
                sftp.put(local, remote)
                
        sftp.close()
        
        print("Running migration script...")
        # Use the correct DB path for remote
        remote_db_path = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"
        
        # Activate venv and run script
        cmd = f"cd {remote_base} && source venv/bin/activate && python tools/migrate_file_manager_isolation.py {remote_db_path}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("Migration Output:")
        print(out)
        if err:
            print("Migration Error:")
            print(err)
            
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        if stderr.read():
             print("Service restart warning/error:", stderr.read().decode())
        else:
             print("Service restarted successfully.")
             
        ssh.close()
        return True
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    deploy_updates()
