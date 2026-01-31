
import paramiko
import os
import sys
import time

# SSH Credentials
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_TEMPLATES_DIR = r'c:\SDG\server\templates'
REMOTE_TEMPLATES_DIR = '/var/www/sustainage/server/templates'

def deploy_templates():
    print(f"Connecting to {HOST}...")
    try:
        transport = paramiko.Transport((HOST, 22))
        transport.connect(username=USER, password=PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Connected.")
        
        # Ensure remote directory exists
        try:
            sftp.stat(REMOTE_TEMPLATES_DIR)
        except FileNotFoundError:
            print(f"Creating remote directory {REMOTE_TEMPLATES_DIR}")
            ssh.exec_command(f"mkdir -p {REMOTE_TEMPLATES_DIR}")
            time.sleep(1)

        # Walk through local templates directory
        print(f"Syncing templates from {LOCAL_TEMPLATES_DIR} to {REMOTE_TEMPLATES_DIR}...")
        for root, dirs, files in os.walk(LOCAL_TEMPLATES_DIR):
            # Create remote subdirectories if needed
            rel_path = os.path.relpath(root, LOCAL_TEMPLATES_DIR)
            if rel_path == '.':
                remote_root = REMOTE_TEMPLATES_DIR
            else:
                remote_root = os.path.join(REMOTE_TEMPLATES_DIR, rel_path).replace('\\', '/')
                try:
                    sftp.stat(remote_root)
                except FileNotFoundError:
                    print(f"Creating remote subdir: {remote_root}")
                    sftp.mkdir(remote_root)
            
            for file in files:
                local_path = os.path.join(root, file)
                remote_path = os.path.join(remote_root, file).replace('\\', '/')
                
                print(f"Uploading {file}...")
                sftp.put(local_path, remote_path)
        
        print("Templates synced successfully.")
        
        # Restart service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

        sftp.close()
        transport.close()
        ssh.close()
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    deploy_templates()
