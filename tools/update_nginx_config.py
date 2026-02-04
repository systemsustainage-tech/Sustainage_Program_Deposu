import os
import sys
import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def update_nginx():
    print("Updating Nginx configuration...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        key_path = KEY_FILE if os.path.exists(KEY_FILE) else None
        if not key_path:
             print(f"Warning: Default SSH key not found at {KEY_FILE}")

        ssh.connect(HOST, username=USER, key_filename=key_path)
        sftp = ssh.open_sftp()
        
        # 1. Upload config
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_path = os.path.join(base_dir, 'deploy', 'sustainage.nginx')
        remote_tmp = '/tmp/sustainage.nginx'
        
        if not os.path.exists(local_path):
            print(f"Error: Local file not found: {local_path}")
            return

        print(f"Uploading {local_path} to {remote_tmp}...")
        sftp.put(local_path, remote_tmp)
        
        # 2. Move and reload
        commands = [
            'cp /tmp/sustainage.nginx /etc/nginx/sites-available/sustainage',
            'ln -sf /etc/nginx/sites-available/sustainage /etc/nginx/sites-enabled/',
            'nginx -t',
            'systemctl reload nginx',
            'systemctl restart sustainage'
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            
            if out: print(out)
            if err: print(f"STDERR: {err}")
            
            if exit_status != 0:
                print(f"Error executing {cmd}: Exit code {exit_status}")
                return
                
        print("Nginx configuration updated and services restarted successfully.")
        ssh.close()
    except Exception as e:
        print(f"Failed to update Nginx: {e}")

if __name__ == "__main__":
    update_nginx()
