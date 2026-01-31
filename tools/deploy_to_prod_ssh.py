import paramiko
import sys
import os

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = "Z/2m?-JDp5VaX6q+HO(b"
REMOTE_APP_DIR = "/var/www/sustainage/SDG_WEB"

def create_sftp_client(client):
    sftp = client.open_sftp()
    return sftp

def upload_file(sftp, local_path, remote_path):
    try:
        sftp.put(local_path, remote_path)
        print(f"Uploaded {local_path} -> {remote_path}")
    except Exception as e:
        print(f"Failed to upload {remote_path}: {e}")

def upload_recursive(sftp, local_path, remote_base):
    for root, dirs, files in os.walk(local_path):
        # Filter hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        rel_path = os.path.relpath(root, local_path).replace('\\', '/')
        if rel_path == '.':
            remote_path = remote_base
        else:
            remote_path = f"{remote_base}/{rel_path}"
            
        try:
            sftp.stat(remote_path)
        except IOError:
            try:
                sftp.mkdir(remote_path)
                print(f"Created directory {remote_path}")
            except:
                pass
        
        for file in files:
            if file.startswith('.'): continue
            
            l_file = os.path.join(root, file)
            r_file = f"{remote_path}/{file}"
            upload_file(sftp, l_file, r_file)

def main():
    try:
        print(f"Connecting to {HOSTNAME}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        sftp = create_sftp_client(client)
        
        # 1. Upload web_app.py
        print("Uploading web_app.py...")
        upload_file(sftp, 'c:/SDG/server/web_app.py', f'{REMOTE_APP_DIR}/web_app.py')

        # 2. Upload backend (excluding data)
        print("Uploading backend...")
        for root, dirs, files in os.walk('c:/SDG/server/backend'):
            # Filter excluded dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'data' and d != '__pycache__']
            
            rel_path = os.path.relpath(root, 'c:/SDG/server/backend').replace('\\', '/')
            if rel_path == '.':
                remote_path = f'{REMOTE_APP_DIR}/backend'
            else:
                remote_path = f'{REMOTE_APP_DIR}/backend/{rel_path}'
                
            try:
                sftp.stat(remote_path)
            except IOError:
                try:
                    sftp.mkdir(remote_path)
                    print(f"Created directory {remote_path}")
                except:
                    pass
            
            for file in files:
                if file.startswith('.') or file.endswith('.pyc'): continue
                l_file = os.path.join(root, file)
                r_file = f"{remote_path}/{file}"
                upload_file(sftp, l_file, r_file)

        # 3. Upload templates
        print("Uploading templates...")
        upload_recursive(sftp, 'c:/SDG/server/templates', f'{REMOTE_APP_DIR}/templates')
        
        sftp.close()
        
        # 3. Restart service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
