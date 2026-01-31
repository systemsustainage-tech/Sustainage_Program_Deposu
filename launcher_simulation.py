import paramiko
import os
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_simulation():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        local_path = 'c:/SUSTAINAGESERVER/tools/simulate_full_usage_remote.py'
        remote_path = '/var/www/sustainage/tools/simulate_full_usage_remote.py'
        
        print(f"Uploading {local_path}...")
        sftp.put(local_path, remote_path)
        
        print("Executing simulation...")
        # We run it with python3 from /var/www/sustainage
        command = "cd /var/www/sustainage && python3 tools/simulate_full_usage_remote.py"
        
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Stream output
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end='')
            if stderr.channel.recv_ready():
                print(stderr.channel.recv(1024).decode(), end='')
            time.sleep(0.1)
            
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    run_simulation()
