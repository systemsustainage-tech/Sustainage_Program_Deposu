import paramiko
import sys
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def upload_and_run(local_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    filename = os.path.basename(local_path)
    remote_tmp_path = f'/tmp/{filename}'
    
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        print(f"Uploading {local_path} to {remote_tmp_path}...")
        sftp.put(local_path, remote_tmp_path)
        sftp.close()
        
        print(f"Executing {remote_tmp_path}...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_tmp_path}")
        
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end='')
            if stderr.channel.recv_ready():
                print(stderr.channel.recv(1024).decode(), end='')
            time.sleep(0.1)
            
        print(stdout.read().decode(), end='')
        print(stderr.read().decode(), end='')
        
        exit_status = stdout.channel.recv_exit_status()
        print(f"\nExit status: {exit_status}")
        
    except Exception as e:
        print(f"Operation failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_and_run.py <local_script_path>")
        sys.exit(1)
    
    upload_and_run(sys.argv[1])
