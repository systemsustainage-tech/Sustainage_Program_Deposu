import paramiko
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy_and_run():
    print("Connecting...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASS)
    
    sftp = client.open_sftp()
    
    local_path = r'c:\SDG\tools\populate_test_data.py'
    remote_path = '/var/www/sustainage/populate_test_data.py'
    
    print(f"Uploading {local_path} to {remote_path}...")
    sftp.put(local_path, remote_path)
    sftp.close()
    
    print("Running script...")
    stdin, stdout, stderr = client.exec_command(f'python3 {remote_path}')
    
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    print("Output:")
    print(out)
    if err:
        print("Errors:")
        print(err)
        
    client.close()

if __name__ == '__main__':
    deploy_and_run()