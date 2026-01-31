import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\locales\\tr.json', 'remote': '/var/www/sustainage/locales/tr.json'},
    {'local': 'c:\\SUSTAINAGESERVER\\locales\\en.json', 'remote': '/var/www/sustainage/locales/en.json'}
]

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = client.open_sftp()
        
        for item in FILES_TO_UPLOAD:
            local_path = item['local']
            remote_path = item['remote']
            print(f"Uploading {local_path} -> {remote_path}")
            sftp.put(local_path, remote_path)
            
        sftp.close()
        
        print("Restarting services...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Services restarted successfully.")
        else:
            print("Error restarting services:")
            print(stderr.read().decode())
            
        client.close()
        print("Deployment complete.")
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
