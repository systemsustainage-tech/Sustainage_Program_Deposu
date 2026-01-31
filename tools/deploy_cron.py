
import paramiko
import os
import sys

# Remote Server Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_BASE_DIR = '/var/www/sustainage'
REMOTE_TOOLS_DIR = f'{REMOTE_BASE_DIR}/tools'

# Files to upload
FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\tools\\setup_cron.sh', 'remote': f'{REMOTE_TOOLS_DIR}/setup_cron.sh'},
    {'local': 'c:\\SUSTAINAGESERVER\\tools\\sustainage_backup.sh', 'remote': f'{REMOTE_TOOLS_DIR}/sustainage_backup.sh'},
    {'local': 'c:\\SUSTAINAGESERVER\\tools\\log_monitor.py', 'remote': f'{REMOTE_TOOLS_DIR}/log_monitor.py'}
]

def run_command(ssh, command):
    print(f"Running command: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    
    if out:
        print(f"Output:\n{out}")
    if err:
        print(f"Error:\n{err}")
    
    if exit_status != 0:
        print(f"Command failed with exit status {exit_status}")
    return exit_status

def deploy_and_run():
    print(f"Connecting to {HOSTNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()
        
        # 1. Upload files
        print("Uploading files...")
        for item in FILES_TO_UPLOAD:
            local_path = item['local']
            remote_path = item['remote']
            print(f"Uploading {local_path} -> {remote_path}")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
        
        sftp.close()
        
        # 2. Set permissions
        print("Setting permissions...")
        run_command(ssh, f"chmod +x {REMOTE_TOOLS_DIR}/setup_cron.sh")
        run_command(ssh, f"chmod +x {REMOTE_TOOLS_DIR}/sustainage_backup.sh")
        # log_monitor.py execution permission is optional if run via python3, but good to have
        run_command(ssh, f"chmod +x {REMOTE_TOOLS_DIR}/log_monitor.py")
        
        # 3. Convert line endings (DOS to Unix) just in case
        print("Converting line endings...")
        run_command(ssh, f"sed -i 's/\r$//' {REMOTE_TOOLS_DIR}/setup_cron.sh")
        run_command(ssh, f"sed -i 's/\r$//' {REMOTE_TOOLS_DIR}/sustainage_backup.sh")
        
        # 4. Run setup script
        print("Executing setup_cron.sh...")
        run_command(ssh, f"bash {REMOTE_TOOLS_DIR}/setup_cron.sh")
        
        print("Deployment and execution completed.")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_and_run()
