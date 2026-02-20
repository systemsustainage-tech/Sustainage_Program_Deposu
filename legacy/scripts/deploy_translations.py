import paramiko
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'
remote_base = '/var/www/sustainage'

files_to_deploy = [
    ('c:/SUSTAINAGESERVER/locales/tr.json', 'locales/tr.json'),
    ('c:/SUSTAINAGESERVER/backend/config/translations_tr.json', 'backend/config/translations_tr.json')
]

def deploy():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password)
        sftp = ssh.open_sftp()
        
        # Ensure remote directories exist
        try: sftp.mkdir(f"{remote_base}/locales")
        except: pass
        try: sftp.mkdir(f"{remote_base}/backend/config")
        except: pass
        
        for local_path, remote_rel_path in files_to_deploy:
            remote_path = f"{remote_base}/{remote_rel_path}"
            print(f"Uploading {local_path} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
                print("Success.")
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
        
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage.service')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Deploy complete.")
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    deploy()
