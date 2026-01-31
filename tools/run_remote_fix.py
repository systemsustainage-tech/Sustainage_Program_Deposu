import paramiko
import os
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_fix():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")

        sftp = client.open_sftp()
        local_file = r'C:\SUSTAINAGESERVER\tools\fix_remote_super_user.py'
        remote_file = '/var/www/sustainage/tools/fix_remote_super_user.py'
        
        print(f"Uploading {local_file}...")
        try:
            client.exec_command('mkdir -p /var/www/sustainage/tools')
        except: pass
        
        sftp.put(local_file, remote_file)
        sftp.close()
        
        print("Running fix script...")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_file}')
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("Output:", out)
        if err:
            print("Error:", err)
            
        client.close()
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    run_fix()
