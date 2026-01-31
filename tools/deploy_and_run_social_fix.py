
import paramiko
import os
import time

def deploy_and_run_fix():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    local_fix_script = r'c:\SUSTAINAGESERVER\tools\fix_social_schema.py'
    remote_fix_script = '/var/www/sustainage/tools/fix_social_schema.py'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        
        sftp = client.open_sftp()
        
        # Ensure tools directory exists
        try:
            sftp.stat('/var/www/sustainage/tools')
        except FileNotFoundError:
            client.exec_command('mkdir -p /var/www/sustainage/tools')
            
        print(f"Uploading {local_fix_script} to {remote_fix_script}...")
        sftp.put(local_fix_script, remote_fix_script)
        sftp.close()
        
        print("Running fix script...")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_fix_script}')
        
        exit_status = stdout.channel.recv_exit_status()
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("Output:")
        print(out)
        
        if err:
            print("Errors:")
            print(err)
            
        if exit_status == 0:
            print("Fix script executed successfully.")
        else:
            print(f"Fix script failed with exit code {exit_status}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_and_run_fix()
