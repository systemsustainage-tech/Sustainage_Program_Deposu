
import paramiko
import os

def deploy_translations():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage'
    
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        files = [
            ('locales/tr.json', 'locales/tr.json'),
            ('locales/en.json', 'locales/en.json')
        ]
        
        for local, remote in files:
            local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', local))
            remote_path = f"{remote_dir}/{remote}"
            
            print(f"Uploading {local} to {remote_path}...")
            sftp.put(local_path, remote_path)
            
        print("Uploads complete. Restarting service to load new translations...")
        client.exec_command('systemctl restart sustainage')
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_translations()
