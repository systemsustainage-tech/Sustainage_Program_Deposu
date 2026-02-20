import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def deploy_fix():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        except:
            print("Key failed, trying password...")
            ssh.connect(HOST, username=USER, password='321')

        sftp = ssh.open_sftp()
        
        # Define paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        rel_path = 'backend/modules/social/social_manager.py'
        local_path = os.path.join(base_dir, rel_path)
        remote_path = f'/var/www/sustainage/{rel_path}'
        
        if not os.path.exists(local_path):
            print(f"Error: Local file not found: {local_path}")
            return

        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        print("Upload successful.")
        
        # Restart service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        # Check status again
        stdin, stdout, stderr = ssh.exec_command("systemctl status sustainage | grep Active")
        print(f"Status: {stdout.read().decode().strip()}")

        sftp.close()
        ssh.close()
        
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    deploy_fix()
