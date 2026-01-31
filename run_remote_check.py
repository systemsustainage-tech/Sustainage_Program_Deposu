import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_DIR = '/var/www/sustainage'

def run_check():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        
        sftp = client.open_sftp()
        sftp.put('C:\\SUSTAINAGESERVER\\check_remote_users.py', f'{REMOTE_DIR}/check_remote_users.py')
        sftp.close()
        
        stdin, stdout, stderr = client.exec_command(f"python3 {REMOTE_DIR}/check_remote_users.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_check()
