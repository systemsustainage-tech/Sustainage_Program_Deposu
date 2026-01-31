import paramiko
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

import sys

FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\web_app.py', 'remote': '/var/www/sustainage/web_app.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\sdg.html', 'remote': '/var/www/sustainage/templates/sdg.html'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\500.html', 'remote': '/var/www/sustainage/templates/500.html'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\404.html', 'remote': '/var/www/sustainage/templates/404.html'}
]

def deploy():
    # If arguments are provided, use them instead of hardcoded list
    files_to_deploy = []
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            # Convert local relative path to absolute and remote path
            # Assume run from project root or tools dir
            # arg: tools/monitor_logs.py
            
            # Normalize path
            arg = arg.replace('/', '\\')
            
            # If absolute, keep it. If relative, join with current cwd (which should be project root)
            if os.path.isabs(arg):
                local_path = arg
            else:
                # Assuming script run from project root, so arg is relative to root
                # But wait, script is in tools/. If run from root, os.getcwd() is root.
                local_path = os.path.abspath(arg)
            
            # Calculate remote path
            # Remove c:\SUSTAINAGESERVER from local path to get relative part
            # This is fragile if paths differ.
            # Better approach: Just assume structure matches /var/www/sustainage/
            
            if 'SUSTAINAGESERVER' in local_path:
                rel_path = local_path.split('SUSTAINAGESERVER\\')[1]
            else:
                # Fallback or error
                print(f"Skipping {local_path} - not in SUSTAINAGESERVER")
                continue
                
            remote_path = '/var/www/sustainage/' + rel_path.replace('\\', '/')
            files_to_deploy.append({'local': local_path, 'remote': remote_path})
    else:
        files_to_deploy = FILES_TO_UPLOAD

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    sftp = client.open_sftp()
    
    for item in files_to_deploy:
        local_path = item['local']
        remote_path = item['remote']
        print(f"Uploading {local_path} to {remote_path}...")
        
        # Ensure remote directory exists
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.stat(remote_dir)
        except IOError:
            # Recursive creation not simple with sftp, but let's try a simple mkdir
            # or execute command
            print(f"Creating directory {remote_dir}...")
            client.exec_command(f"mkdir -p {remote_dir}")
            time.sleep(1) # Wait for mkdir
            
        try:
            sftp.put(local_path, remote_path)
        except Exception as e:
            print(f"Failed to upload {local_path}: {e}")
    
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

if __name__ == "__main__":
    deploy()
