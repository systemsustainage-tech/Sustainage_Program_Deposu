
import paramiko
import sys

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_file = '/var/www/sustainage/backend/modules/prioritization/prioritization_manager.py'

def cat_remote_file():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print(f"Reading {remote_file}...")
        stdin, stdout, stderr = ssh.exec_command(f"grep -A 50 'def add_survey_question' {remote_file}")
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("STDOUT:")
        print(out)
        if err:
            print("STDERR:")
            print(err)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    cat_remote_file()
