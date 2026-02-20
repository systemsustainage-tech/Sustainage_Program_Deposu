import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy_fix():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        sftp = client.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\setup_test_user.py'
        remote_path = '/var/www/sustainage/setup_test_user.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()
        
        print("Running setup_test_user.py...")
        stdin, stdout, stderr = client.exec_command(f"/var/www/sustainage/venv/bin/python {remote_path}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_fix()