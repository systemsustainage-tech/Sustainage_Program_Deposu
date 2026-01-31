import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def run_remote_verify():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    sftp = ssh.open_sftp()
    local_path = r'c:\SDG\tools\remote_verify_translation.py'
    remote_path = '/var/www/sustainage/remote_verify_translation.py'
    sftp.put(local_path, remote_path)
    sftp.close()
    
    stdin, stdout, stderr = ssh.exec_command(f"/var/www/sustainage/venv/bin/python3 {remote_path}")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.exec_command(f"rm {remote_path}")
    ssh.close()

if __name__ == "__main__":
    run_remote_verify()
