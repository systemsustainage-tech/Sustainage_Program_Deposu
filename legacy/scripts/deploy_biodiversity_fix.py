import paramiko
import os
import time

# Server Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

REMOTE_DIR = '/var/www/sustainage'

FILES_TO_UPLOAD = [
    ('templates/biodiversity.html', f'{REMOTE_DIR}/templates/biodiversity.html'),
    ('templates/economic.html', f'{REMOTE_DIR}/templates/economic.html'),
    ('web_app.py', f'{REMOTE_DIR}/web_app.py'),
    ('backend/modules/economic/economic_value_manager.py', f'{REMOTE_DIR}/backend/modules/economic/economic_value_manager.py'),
]

def deploy():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # Upload files
        for local, remote in FILES_TO_UPLOAD:
            local_path = os.path.join(os.getcwd(), local)
            if not os.path.exists(local_path):
                print(f"Warning: Local file not found: {local_path}")
                continue
                
            print(f"Uploading {local} to {remote}...")
            try:
                # Ensure remote directory exists
                remote_dir = os.path.dirname(remote)
                try:
                    sftp.stat(remote_dir)
                except IOError:
                    print(f"Creating directory: {remote_dir}")
                    sftp.mkdir(remote_dir)
                    
                sftp.put(local_path, remote)
            except Exception as e:
                print(f"Error uploading {local}: {e}")
        
        sftp.close()
        
        # Restart Service
        print("Restarting sustainage service...")
        
        # Restart systemd service
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print("Service restarted successfully via systemctl.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")
            # Manual restart fallback
            print("Attempting manual restart...")
            client.exec_command("pkill -f 'python web_app.py'")
            time.sleep(1)
            
            # Check for venv
            venv_python = f"{REMOTE_DIR}/venv/bin/python"
            stdin, stdout, stderr = client.exec_command(f"ls {venv_python}")
            if stdout.channel.recv_exit_status() != 0:
                print("Venv python not found, using global python3")
                venv_python = "python3"
            
            start_cmd = f"cd {REMOTE_DIR} && nohup {venv_python} web_app.py > app.log 2>&1 &"
            print(f"Running: {start_cmd}")
            client.exec_command(start_cmd)
            
        # Check status
        time.sleep(3)
        stdin, stdout, stderr = client.exec_command("ps aux | grep web_app.py | grep -v grep")
        print("Running processes:")
        print(stdout.read().decode())
        
        # Verify 200 OK on key modules
        print("Verifying modules...")
        check_script = """
import requests
import sys

def check(url, name):
    try:
        r = requests.get(url, timeout=5)
        print(f"{name}: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"{name}: Error {e}")
        return False

base = "http://localhost:5000"
check(f"{base}/biodiversity", "Biodiversity")
check(f"{base}/economic", "Economic")
"""
        stdin, stdout, stderr = client.exec_command(f"python3 -c '{check_script}'")
        print(stdout.read().decode())
        print(stderr.read().decode())

    except Exception as e:
        print(f"Deploy failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
