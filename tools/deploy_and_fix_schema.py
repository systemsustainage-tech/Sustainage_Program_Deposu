import paramiko
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Kayra_1507'

FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\tools\\fix_remote_schema_v2.py', 'remote': '/var/www/sustainage/tools/fix_remote_schema_v2.py'}
]

def deploy_and_run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    except paramiko.AuthenticationException:
        print("Authentication failed with 'Kayra_1507'. Trying alternate password...")
        client.connect(HOSTNAME, username=USERNAME, password='Z/2m?-JDp5VaX6q+HO(b')

    sftp = client.open_sftp()
    
    for item in FILES_TO_UPLOAD:
        local_path = item['local']
        remote_path = item['remote']
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
    
    sftp.close()
    
    print("Running fix_remote_schema_v2.py...")
    stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/fix_remote_schema_v2.py")
    
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    print("Output:")
    print(out)
    if err:
        print("Errors:")
        print(err)
        
    print("Restarting services...")
    stdin, stdout, stderr = client.exec_command("systemctl restart sustainage && pkill -HUP gunicorn")
    print(stdout.read().decode())
    
    client.close()

if __name__ == "__main__":
    deploy_and_run()
