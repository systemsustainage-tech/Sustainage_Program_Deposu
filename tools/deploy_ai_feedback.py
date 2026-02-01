import paramiko
import os
import sys

# Server details
HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"
REMOTE_BASE = "/var/www/sustainage"

FILES = [
    ("backend/modules/ai/ai_manager.py", "backend/modules/ai/ai_manager.py"),
    ("web_app.py", "web_app.py"),
    ("templates/ai_reports.html", "templates/ai_reports.html")
]

def deploy():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        for local, remote in FILES:
            local_path = os.path.abspath(local)
            remote_path = f"{REMOTE_BASE}/{remote}"
            
            if not os.path.exists(local_path):
                print(f"Error: Local file {local_path} not found!")
                continue

            print(f"Uploading {local} -> {remote_path}...")
            sftp.put(local_path, remote_path)
        
        sftp.close()
        
        # Restart service
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

if __name__ == "__main__":
    deploy()
