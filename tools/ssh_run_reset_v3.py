import paramiko
import logging

logging.basicConfig(level=logging.INFO)

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    sftp = client.open_sftp()
    local_path = 'c:/SDG/tools/ssh_reset_super_password_v3.py'
    remote_path = '/var/www/sustainage/reset_super_v3.py'
    sftp.put(local_path, remote_path)
    sftp.close()
    
    logging.info("Running reset script v3...")
    stdin, stdout, stderr = client.exec_command(f"/var/www/sustainage/venv/bin/python3 {remote_path}")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    client.close()

if __name__ == "__main__":
    main()
