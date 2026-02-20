import paramiko
import os
import time

# Server Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

REMOTE_DIR = '/var/www/sustainage'
TEMPLATES_DIR = f'{REMOTE_DIR}/templates'
SERVICES_DIR = f'{REMOTE_DIR}/services'

FILES_TO_UPLOAD = [
    ('.env', f'{REMOTE_DIR}/.env'),
    ('services/__init__.py', f'{SERVICES_DIR}/__init__.py'),
    ('services/icons.py', f'{SERVICES_DIR}/icons.py'),
    ('services/email_service.py', f'{SERVICES_DIR}/email_service.py'),
    ('web_app.py', f'{REMOTE_DIR}/web_app.py'),
    ('templates/login.html', f'{TEMPLATES_DIR}/login.html'),
    ('templates/forgot_password.html', f'{TEMPLATES_DIR}/forgot_password.html'),
    ('templates/verify_code.html', f'{TEMPLATES_DIR}/verify_code.html'),
    ('templates/reset_password.html', f'{TEMPLATES_DIR}/reset_password.html'),
    ('create_reset_table.py', f'{REMOTE_DIR}/create_reset_table.py')
]

def deploy():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # Create services directory
        try:
            sftp.mkdir(SERVICES_DIR)
            print("Created services directory.")
        except IOError:
            print("Services directory likely already exists.")
            
        # Upload files
        for local, remote in FILES_TO_UPLOAD:
            local_path = os.path.join(os.getcwd(), local)
            print(f"Uploading {local} to {remote}...")
            try:
                sftp.put(local_path, remote)
            except Exception as e:
                print(f"Error uploading {local}: {e}")
        
        sftp.close()
        
        # Run DB update (just in case)
        print("Running DB schema update (create_reset_table.py)...")
        stdin, stdout, stderr = client.exec_command(f"python3 {REMOTE_DIR}/create_reset_table.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err: print(f"DB Error: {err}")
        
        # Restart Service
        print("Restarting sustainage service...")
        # First try to stop any existing instances
        client.exec_command("pkill -f 'python web_app.py'")
        client.exec_command("pkill -f 'python3 web_app.py'")
        
        # Try systemd restart
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print("Service restarted successfully via systemctl.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")
            # Fallback: try to find and kill python process if systemd fails
            print("Attempting manual restart using venv...")
            
            # Check for venv
            venv_python = f"{REMOTE_DIR}/venv/bin/python"
            # If venv python doesn't exist, fall back to python3
            stdin, stdout, stderr = client.exec_command(f"ls {venv_python}")
            if stdout.channel.recv_exit_status() != 0:
                print("Venv python not found, using global python3")
                venv_python = "python3"
            
            start_cmd = f"nohup {venv_python} {REMOTE_DIR}/web_app.py > {REMOTE_DIR}/app.log 2>&1 &"
            print(f"Running: {start_cmd}")
            client.exec_command(start_cmd)
            
            time.sleep(3)
            # Check if running
            stdin, stdout, stderr = client.exec_command("ps aux | grep web_app.py | grep -v grep")
            if stdout.channel.recv_exit_status() == 0:
                print("Manual start successful. Process is running.")
                print(stdout.read().decode())
            else:
                print("Manual start FAILED. Checking log:")
                stdin, stdout, stderr = client.exec_command(f"tail -n 20 {REMOTE_DIR}/app.log")
                print(stdout.read().decode())
                
        client.close()
        print("Deployment complete.")

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
