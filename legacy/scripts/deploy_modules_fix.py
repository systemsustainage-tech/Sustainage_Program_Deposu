import paramiko
import os
import time

# Server Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

REMOTE_DIR = '/var/www/sustainage'
BACKEND_DIR = f'{REMOTE_DIR}/backend'
MODULES_DIR = f'{BACKEND_DIR}/modules'

FILES_TO_UPLOAD = [
    ('web_app.py', f'{REMOTE_DIR}/web_app.py'),
    ('fix_rate_limit_table.py', f'{REMOTE_DIR}/fix_rate_limit_table.py'),
    ('backend/modules/tnfd/tnfd_manager.py', f'{MODULES_DIR}/tnfd/tnfd_manager.py'),
    ('backend/modules/tnfd/__init__.py', f'{MODULES_DIR}/tnfd/__init__.py'),
    ('backend/modules/tcfd/tcfd_manager.py', f'{MODULES_DIR}/tcfd/tcfd_manager.py'),
    ('backend/modules/cdp/cdp_manager.py', f'{MODULES_DIR}/cdp/cdp_manager.py'),
    ('backend/modules/environmental/waste_manager.py', f'{BACKEND_DIR}/modules/environmental/waste_manager.py'),
]

DIRECTORIES_TO_CREATE = [
    f'{MODULES_DIR}/tnfd',
    f'{MODULES_DIR}/tcfd',
    f'{MODULES_DIR}/cdp'
]

def deploy():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # Create directories
        for remote_dir in DIRECTORIES_TO_CREATE:
            try:
                # Try to stat the directory to see if it exists
                try:
                    sftp.stat(remote_dir)
                    print(f"Directory exists: {remote_dir}")
                except IOError:
                    # Directory doesn't exist, create it
                    print(f"Creating directory: {remote_dir}")
                    sftp.mkdir(remote_dir)
            except Exception as e:
                print(f"Error checking/creating directory {remote_dir}: {e}")

        # Upload files
        for local, remote in FILES_TO_UPLOAD:
            local_path = os.path.join(os.getcwd(), local)
            if not os.path.exists(local_path):
                print(f"Warning: Local file not found: {local_path}")
                continue
                
            print(f"Uploading {local} to {remote}...")
            try:
                sftp.put(local_path, remote)
            except Exception as e:
                print(f"Error uploading {local}: {e}")
        
        sftp.close()
        
        # Run DB Fix
        print("Running DB Fix...")
        stdin, stdout, stderr = client.exec_command(f"python3 {REMOTE_DIR}/fix_rate_limit_table.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err: print(f"DB Fix Error: {err}")

        # Verify web_app.py update
        print("Verifying web_app.py update...")
        stdin, stdout, stderr = client.exec_command(f"grep 'sustainage_secret_key_fixed' {REMOTE_DIR}/web_app.py")
        verification = stdout.read().decode().strip()
        if verification:
            print(f"✅ web_app.py updated successfully: {verification}")
        else:
            print("❌ web_app.py update FAILED! Secret key not found.")
        
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

    except Exception as e:
        print(f"Deploy failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
