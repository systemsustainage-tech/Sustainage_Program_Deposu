import paramiko
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
local_file = 'c:\\SUSTAINAGESERVER\\tools\\reinit_tsrs_remote.py'
remote_file = '/var/www/sustainage/tools/reinit_tsrs_remote.py'

def upload_and_run():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        print("Connected.")
        
        # SFTP Upload
        sftp = ssh.open_sftp()
        print(f"Uploading {local_file} to {remote_file}...")
        sftp.put(local_file, remote_file)
        sftp.close()
        print("Upload complete.")
        
        # Run script
        command = f"cd /var/www/sustainage && /var/www/sustainage/venv/bin/python tools/reinit_tsrs_remote.py"
        print(f"Running command: {command}")
        
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print("Output:")
        print(output)
        
        if error:
            print("Error:")
            print(error)
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_and_run()
