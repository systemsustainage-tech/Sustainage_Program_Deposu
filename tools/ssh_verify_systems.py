import paramiko
import os

HOST = "185.73.54.215"
USER = "root"
PASS = "27112024Aa."

def verify_systems():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    sftp = ssh.open_sftp()
    local_path = r'c:\SDG\tools\remote_verify.py'
    remote_path = '/var/www/sustainage/remote_verify.py'
    sftp.put(local_path, remote_path)
    sftp.close()
    
    stdin, stdout, stderr = ssh.exec_command(f"/var/www/sustainage/venv/bin/python3 {remote_path}")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.exec_command(f"rm {remote_path}")
    ssh.close()

if __name__ == "__main__":
    verify_systems()
