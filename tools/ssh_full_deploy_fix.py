
import paramiko
import os
import sys
import time
import stat

# SSH Credentials
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_BASE = r'c:\SDG'
REMOTE_BASE = '/var/www/sustainage'

def upload_dir(sftp, local_dir, remote_dir):
    try:
        try:
            sftp.stat(remote_dir)
        except IOError:
            print(f"Creating remote dir: {remote_dir}")
            sftp.mkdir(remote_dir)
            
        for item in os.listdir(local_dir):
            if item in ['.git', '__pycache__', 'venv', 'logs', 'node_modules', '.DS_Store']:
                continue
                
            local_path = os.path.join(local_dir, item)
            remote_path = remote_dir + '/' + item
            
            if os.path.isfile(local_path):
                print(f"Uploading {item} to {remote_path}")
                sftp.put(local_path, remote_path)
            elif os.path.isdir(local_path):
                upload_dir(sftp, local_path, remote_path)
                
    except Exception as e:
        print(f"Error uploading {local_dir}: {e}")

def fix_permissions(ssh):
    print("Fixing permissions...")
    
    # 1. Fix Gunicorn executable
    gunicorn_path = "/var/www/sustainage/venv/bin/gunicorn"
    print(f"Making {gunicorn_path} executable...")
    ssh.exec_command(f"chmod +x {gunicorn_path}")
    
    # 2. Fix other bin files
    ssh.exec_command("chmod +x /var/www/sustainage/venv/bin/*")
    
    # 3. Fix ownership
    ssh.exec_command(f"chown -R www-data:www-data {REMOTE_BASE}")
    
    # 4. Standard permissions
    ssh.exec_command(f"find {REMOTE_BASE} -type d -exec chmod 755 {{}} +")
    ssh.exec_command(f"find {REMOTE_BASE} -type f -exec chmod 644 {{}} +")
    
    # 5. Re-apply executable to bin (find -type f chmod 644 removed it)
    ssh.exec_command(f"chmod +x {gunicorn_path}")
    ssh.exec_command("chmod +x /var/www/sustainage/venv/bin/*")

def main():
    print(f"Connecting to {HOST}...")
    try:
        transport = paramiko.Transport((HOST, 22))
        transport.connect(username=USER, password=PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Connected.")
        
        # 1. Upload web_app.py to ROOT
        print("Uploading web_app.py...")
        sftp.put(os.path.join(LOCAL_BASE, 'server', 'web_app.py'), REMOTE_BASE + '/web_app.py')
        
        # 2. Upload Backend (CRITICAL)
        print("Uploading backend...")
        upload_dir(sftp, os.path.join(LOCAL_BASE, 'server', 'backend'), REMOTE_BASE + '/backend')
        
        # 3. Upload Templates (CRITICAL)
        print("Uploading templates...")
        upload_dir(sftp, os.path.join(LOCAL_BASE, 'server', 'templates'), REMOTE_BASE + '/templates')
        
        # 4. Upload Config
        print("Uploading config...")
        upload_dir(sftp, os.path.join(LOCAL_BASE, 'server', 'config'), REMOTE_BASE + '/config')

        # 5. Upload Utils/Services if they exist
        if os.path.exists(os.path.join(LOCAL_BASE, 'server', 'utils')):
            print("Uploading utils...")
            upload_dir(sftp, os.path.join(LOCAL_BASE, 'server', 'utils'), REMOTE_BASE + '/utils')
        
        if os.path.exists(os.path.join(LOCAL_BASE, 'server', 'services')):
            print("Uploading services...")
            upload_dir(sftp, os.path.join(LOCAL_BASE, 'server', 'services'), REMOTE_BASE + '/services')

        # 6. Fix Permissions
        fix_permissions(ssh)
        
        # 7. Restart Service
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # 8. Check Status
        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("systemctl status sustainage")
        print(stdout.read().decode())

        sftp.close()
        transport.close()
        ssh.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
