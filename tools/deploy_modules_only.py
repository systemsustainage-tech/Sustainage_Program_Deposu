import paramiko
import os
import sys

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = "Z/2m?-JDp5VaX6q+HO(b"
REMOTE_APP_DIR = "/var/www/sustainage/SDG_WEB"

def upload_file(sftp, local_path, remote_path):
    try:
        sftp.put(local_path, remote_path)
        # print(f"Uploaded {local_path} -> {remote_path}")
        return True
    except Exception as e:
        print(f"Failed to upload {remote_path}: {e}")
        return False

def main():
    print(f"Connecting to {HOSTNAME}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    sftp = client.open_sftp()
    print("Connected.")

    local_base = 'c:/SDG/server/backend/modules'
    remote_base = f'{REMOTE_APP_DIR}/backend/modules'
    
    count = 0
    for root, dirs, files in os.walk(local_base):
        # Filter hidden dirs and pycache
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        rel_path = os.path.relpath(root, local_base).replace('\\', '/')
        if rel_path == '.':
            remote_path = remote_base
        else:
            remote_path = f"{remote_base}/{rel_path}"
            print(f"Entering {rel_path}...")
            
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
            
            # Special check for __init__.py to ensure it's uploaded
            is_init = file == '__init__.py'
            
            if upload_file(sftp, l_file, r_file):
                count += 1
                if is_init:
                    print(f"Updated {file} in {rel_path}")
                elif count % 50 == 0:
                    print(f"Uploaded {count} files... (last: {file})")

    sftp.close()
    
    print("Restarting service...")
    client.exec_command("systemctl restart sustainage")
    print("Done.")

if __name__ == '__main__':
    main()
