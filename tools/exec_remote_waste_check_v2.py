import paramiko
import time
import os

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = "Z/2m?-JDp5VaX6q+HO(b)"

def run_check():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Upload
        sftp = ssh.open_sftp()
        local_path = "c:/SUSTAINAGESERVER/tools/check_waste_schema.py"
        remote_path = "/var/www/sustainage/tools/check_waste_schema.py"
        
        # Ensure remote directory exists
        try:
            sftp.stat("/var/www/sustainage/tools")
        except FileNotFoundError:
            ssh.exec_command("mkdir -p /var/www/sustainage/tools")
            
        sftp.put(local_path, remote_path)
        sftp.close()
        
        # Run
        print(f"Executing {remote_path}...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print("--- OUTPUT ---")
        print(output)
        if error:
            print("--- ERROR ---")
            print(error)
            
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_check()
