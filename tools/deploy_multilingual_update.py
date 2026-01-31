import paramiko
import os

def deploy():
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
        
        # Files to deploy
        # (local_path, remote_path) relative to project root
        files = [
            ('backend/locales/tr.json', 'backend/locales/tr.json'),
            ('backend/locales/de.json', 'backend/locales/de.json'),
            ('backend/locales/fr.json', 'backend/locales/fr.json'),
            ('backend/locales/en.json', 'backend/locales/en.json'),
            ('remote_web_app.py', 'remote_web_app.py'),
            ('templates/base.html', 'templates/base.html')
        ]
        
        base_path = r'c:\SUSTAINAGESERVER'
        
        for local, remote in files:
            local_full = os.path.join(base_path, local)
            remote_full = f"{remote_dir}/{remote}"
            
            # Ensure remote directory exists (e.g. backend/locales)
            # Simple check/creation
            remote_folder = os.path.dirname(remote_full).replace('\\', '/')
            try:
                sftp.stat(remote_folder)
            except IOError:
                print(f"Creating remote directory: {remote_folder}")
                # This is recursive? No. Assuming parent exists.
                # backend/locales should exist.
                pass 

            print(f"Uploading {local} to {remote_full}...")
            sftp.put(local_full, remote_full)
            
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command('systemctl restart sustainage')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    deploy()