import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_DIR = '/var/www/sustainage/templates'

FILES_TO_DEPLOY = [
    'c:\\SUSTAINAGESERVER\\templates\\500.html',
    'c:\\SUSTAINAGESERVER\\templates\\404.html'
]

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = client.open_sftp()
        
        for local_path in FILES_TO_DEPLOY:
            filename = os.path.basename(local_path)
            remote_path = f"{REMOTE_DIR}/{filename}"
            print(f"Uploading {filename}...")
            sftp.put(local_path, remote_path)
            
        sftp.close()
        print("Deployment complete.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
