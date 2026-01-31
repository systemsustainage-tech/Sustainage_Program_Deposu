import paramiko
import os
import time

def run_db_fix():
    hostname = '72.62.150.207'
    username = 'root'
    password = 'Z/2m?-JDp5VaX6q+HO(b)'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        
        sftp = client.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\tools\fix_remote_db_issues.py'
        remote_path = '/var/www/sustainage/tools/fix_remote_db_issues.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        
        # Ensure directory exists
        client.exec_command("mkdir -p /var/www/sustainage/tools")
        client.exec_command("mkdir -p /var/www/sustainage/config")
        
        sftp.put(local_path, remote_path)
        sftp.close()
        
        print("Running DB fix script...")
        cmd = "/var/www/sustainage/venv/bin/python /var/www/sustainage/tools/fix_remote_db_issues.py"
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        print("Waiting for output...")
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("\n--- STDOUT ---")
        print(out)
        print("\n--- STDERR ---")
        print(err)
        
        exit_code = stdout.channel.recv_exit_status()
        print(f"\nFix script finished with exit code: {exit_code}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_db_fix()
