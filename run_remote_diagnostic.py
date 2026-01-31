import paramiko
import os
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

files_to_deploy = [
    ('c:/SUSTAINAGESERVER/tools/check_remote_data.py', 'tools/check_remote_data.py'),
]

def run_diagnostic():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        for local_path, remote_rel_path in files_to_deploy:
            if not os.path.exists(local_path):
                print(f"Local file not found: {local_path}")
                continue
                
            remote_path = f"{remote_base}/{remote_rel_path}"
            print(f"Uploading {local_path} to {remote_path}...")
            sftp.put(local_path, remote_path)
            print("Success.")
                
        sftp.close()

        print("Running check_remote_data.py on remote...")
        stdin, stdout, stderr = ssh.exec_command(f"cd {remote_base} && python3 tools/check_remote_data.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output: {err}")
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_diagnostic()
