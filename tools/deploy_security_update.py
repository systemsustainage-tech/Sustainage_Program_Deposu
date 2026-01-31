
import paramiko
import os
import sys

# Remote Server Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_BASE_DIR = '/var/www/sustainage'

# Files to upload
FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\web_app.py', 'remote': f'{REMOTE_BASE_DIR}/web_app.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\base.html', 'remote': f'{REMOTE_BASE_DIR}/templates/base.html'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\verify_2fa.html', 'remote': f'{REMOTE_BASE_DIR}/templates/verify_2fa.html'},
    {'local': 'c:\\SUSTAINAGESERVER\\docs\\policies\\SOC2_ISO27001_Policies.md', 'remote': f'{REMOTE_BASE_DIR}/docs/policies/SOC2_ISO27001_Policies.md'}
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

def deploy_and_restart():
    print(f"Connecting to {HOSTNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()
        
        # Ensure directories exist
        print("Checking remote directories...")
        try:
            sftp.stat(f'{REMOTE_BASE_DIR}/docs/policies')
        except FileNotFoundError:
            print("Creating remote policies directory...")
            run_command(ssh, f"mkdir -p {REMOTE_BASE_DIR}/docs/policies")

        # Upload files
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
        
        # Restart Service
        print("Restarting SustainAge service...")
        run_command(ssh, "systemctl restart sustainage.service")
        
        print("Deployment completed successfully.")
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_and_restart()
