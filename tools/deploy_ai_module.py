import paramiko
import os
import time

# Remote server configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = os.environ.get('REMOTE_SSH_PASS', 'Kayra_1507')

def deploy_changes():
    """AI Modülü değişikliklerini deploy et"""
    print(f"Connecting to {HOSTNAME}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()
        
        # Dosyaları yükle
        files_to_deploy = [
            {
                "local": r"c:\SUSTAINAGESERVER\backend\modules\ai\ai_manager.py",
                "remote": "/var/www/sustainage/backend/modules/ai/ai_manager.py"
            },
            {
                "local": r"c:\SUSTAINAGESERVER\backend\modules\ai\prompts.py",
                "remote": "/var/www/sustainage/backend/modules/ai/prompts.py"
            }
        ]
        
        for file_info in files_to_deploy:
            print(f"Uploading {os.path.basename(file_info['local'])} to {file_info['remote']}...")
            sftp.put(file_info['local'], file_info['remote'])
            
        sftp.close()
        
        # Servisi yeniden başlat
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        ssh.close()
        print("Deployment completed successfully.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy_changes()
