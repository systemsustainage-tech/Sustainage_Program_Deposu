
import paramiko
import os
import sys
import time

# Server details
HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"
REMOTE_BASE = "/var/www/sustainage"

FILES_TO_DEPLOY = [
    ("backend/modules/esg/esg_manager.py", "backend/modules/esg/esg_manager.py"),
    ("web_app.py", "web_app.py"),
    ("templates/esg.html", "templates/esg.html"),
    ("templates/esg_settings.html", "templates/esg_settings.html"),
    ("backend/modules/stakeholder/stakeholder_engagement.py", "backend/modules/stakeholder/stakeholder_engagement.py")
]

def deploy():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        for local_path, remote_rel_path in FILES_TO_DEPLOY:
            full_local_path = os.path.abspath(local_path)
            full_remote_path = f"{REMOTE_BASE}/{remote_rel_path}"
            
            print(f"Uploading {local_path} -> {full_remote_path}...")
            sftp.put(full_local_path, full_remote_path)
            
        sftp.close()
        
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        ssh.close()
        print("Deployment complete.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy()
