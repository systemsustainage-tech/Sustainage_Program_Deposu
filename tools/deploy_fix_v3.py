import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Kayra_1507'

FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\tools\\fix_remote_schema_v3.py', 'remote': '/var/www/sustainage/tools/fix_remote_schema_v3.py'}
]

def deploy_and_run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    except:
        client.connect(HOSTNAME, username=USERNAME, password='Z/2m?-JDp5VaX6q+HO(b')

    sftp = client.open_sftp()
    
    for item in FILES_TO_UPLOAD:
        local_path = item['local']
        remote_path = item['remote']
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
    
    sftp.close()
    
    print("Running fix_remote_schema_v3.py...")
    stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/tools/fix_remote_schema_v3.py")
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    print("Restarting services...")
    client.exec_command("systemctl restart sustainage && pkill -HUP gunicorn")
    
    client.close()

if __name__ == "__main__":
    deploy_and_run()
