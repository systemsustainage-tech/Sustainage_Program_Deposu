import paramiko
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_verify():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        local_path = 'c:/SUSTAINAGESERVER/tools/verify_logs_remote.py'
        remote_path = '/var/www/sustainage/tools/verify_logs_remote.py'
        
        print(f"Uploading {local_path}...")
        sftp.put(local_path, remote_path)
        
        print("Executing...")
        command = "cd /var/www/sustainage && python3 tools/verify_logs_remote.py"
        stdin, stdout, stderr = ssh.exec_command(command)
        
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    run_verify()
