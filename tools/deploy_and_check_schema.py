import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy_and_check():
    print("Connecting...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASS)
    
    sftp = client.open_sftp()
    
    local_path = r'c:\SDG\tools\check_schema.py'
    remote_path = '/var/www/sustainage/check_schema.py'
    
    print(f"Uploading {local_path} to {remote_path}...")
    sftp.put(local_path, remote_path)
    sftp.close()
    
    print("Running script...")
    stdin, stdout, stderr = client.exec_command(f'python3 {remote_path}')
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    client.close()

if __name__ == '__main__':
    deploy_and_check()
