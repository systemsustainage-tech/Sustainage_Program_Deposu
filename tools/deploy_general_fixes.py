import os
import sys
import paramiko

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def deploy_fixes():
    hostname = "72.62.150.207"
    username = "root"
    key_path = os.path.expanduser("~/.ssh/id_rsa")
    
    remote_base = "/var/www/sustainage"
    
    files_to_deploy = [
        (r"c:\SUSTAINAGESERVER\backend\modules\strategic\sustainability_strategy_manager.py", 
         f"{remote_base}/backend/modules/strategic/sustainability_strategy_manager.py"),
        (r"c:\SUSTAINAGESERVER\remote_web_app.py", 
         f"{remote_base}/remote_web_app.py"),
        (r"c:\SUSTAINAGESERVER\backend\config\database.py", 
         f"{remote_base}/backend/config/database.py"),
        (r"c:\SUSTAINAGESERVER\PLANNED_IMPROVEMENTS.md", 
         f"{remote_base}/PLANNED_IMPROVEMENTS.md")
    ]
    
    print(f"Connecting to {hostname}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if os.path.exists(key_path):
            ssh.connect(hostname, username=username, key_filename=key_path)
        else:
            print(f"Key not found at {key_path}, trying default/agent...")
            ssh.connect(hostname, username=username)
        
        sftp = ssh.open_sftp()
        
        for local, remote in files_to_deploy:
            print(f"Uploading {local} -> {remote}")
            try:
                # Ensure directory exists
                remote_dir = os.path.dirname(remote)
                try:
                    sftp.stat(remote_dir)
                except FileNotFoundError:
                    print(f"Creating directory: {remote_dir}")
                    ssh.exec_command(f"mkdir -p {remote_dir}")
                
                sftp.put(local, remote)
            except Exception as e:
                print(f"Failed to upload {local}: {e}")
                
        sftp.close()
        
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        err = stderr.read().decode()
        if err:
             print("Service restart warning/error:", err)
        else:
             print("Service restarted successfully.")
             
        # Check for DB path confusion
        print("Checking remote database paths...")
        stdin, stdout, stderr = ssh.exec_command("ls -l /var/www/sustainage/backend/data/")
        print(stdout.read().decode())
        
        ssh.close()
        return True
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    deploy_fixes()
