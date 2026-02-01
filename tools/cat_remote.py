
import paramiko
import sys
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Sustainage123!'

def cat_remote_file(remote_path):
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        full_path = f"/var/www/sustainage/{remote_path}"
        print(f"Reading {full_path}...")
        stdin, stdout, stderr = ssh.exec_command(f"cat {full_path}")
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out:
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
    if len(sys.argv) < 2:
        print("Usage: python cat_remote.py <remote_relative_path>")
        sys.exit(1)
    cat_remote_file(sys.argv[1])
