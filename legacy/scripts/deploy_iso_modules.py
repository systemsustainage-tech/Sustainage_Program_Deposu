import paramiko
import os
import sys
import time

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_BASE = '/var/www/sustainage'

FILES_TO_DEPLOY = [
    'web_app.py',
    'templates/human_rights.html',
    'templates/labor.html',
    'templates/fair_operating.html',
    'templates/consumer.html',
    'templates/community.html'
]

def deploy():
    print(f"Starting deployment to {HOSTNAME}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect using SSHClient which handles auth better with look_for_keys=False
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
        print("SSH Connected.")
        
        sftp = ssh.open_sftp()
        
        for file_path in FILES_TO_DEPLOY:
            local_path = os.path.abspath(file_path)
            remote_path = f"{REMOTE_BASE}/{file_path}"
            
            if not os.path.exists(local_path):
                print(f"Warning: Local file not found: {local_path}")
                continue
                
            print(f"Uploading {file_path} -> {remote_path}")
            # Ensure remote directory exists (simple check)
            remote_dir = os.path.dirname(remote_path)
            try:
                sftp.stat(remote_dir)
            except IOError:
                # directory might not exist, but for these files they should (templates/ and root)
                pass 
                
            sftp.put(local_path, remote_path)
            
        sftp.close()
        print("Files uploaded successfully.")
        
        # Restart service
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage.service')
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service. Exit code: {exit_status}")
            print(stderr.read().decode())
            
        ssh.close()
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy()
