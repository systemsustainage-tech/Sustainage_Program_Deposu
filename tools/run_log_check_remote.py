
import paramiko
import sys
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_check():
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        
        # Upload script
        sftp = client.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\tools\check_system_logs_remote.py'
        remote_path = '/var/www/sustainage/tools/check_system_logs_remote.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()

        print("Running check_system_logs_remote.py...")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_path}')
        
        print("Output:")
        print(stdout.read().decode())
        print("Errors:")
        print(stderr.read().decode())
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_remote_check()
