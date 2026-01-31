import paramiko
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy_and_init_db():
    print("Connecting...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASS)
    
    sftp = client.open_sftp()
    
    local_path = r'c:\SDG\tools\create_report_registry.py'
    remote_path = '/var/www/sustainage/create_report_registry.py'
    
    print(f"Uploading {local_path} to {remote_path}...")
    sftp.put(local_path, remote_path)
    sftp.close()
    
    print("Running DB init script...")
    stdin, stdout, stderr = client.exec_command(f'python3 {remote_path}')
    
    # Wait for command to finish and get exit status
    exit_status = stdout.channel.recv_exit_status()
    
    if exit_status == 0:
        print("Script executed successfully.")
        print(stdout.read().decode())
    else:
        print("Script execution failed.")
        print(stderr.read().decode())
        
    client.close()

if __name__ == '__main__':
    deploy_and_init_db()
