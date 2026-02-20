import paramiko
import os
import time

# Server Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'  # deploy_update.py'den alınan şifre

REMOTE_DIR = '/var/www/sustainage'

def deploy_fix():
    print(f"Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # 1. Upload remote_web_app.py as web_app.py
        local_path = os.path.join(os.getcwd(), 'remote_web_app.py')
        remote_path = f'{REMOTE_DIR}/web_app.py'
        
        print(f"Uploading corrected {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        # 2. Upload social templates just in case
        templates = ['social.html', 'social_edit.html']
        for t in templates:
            local_t = os.path.join(os.getcwd(), 'templates', t)
            remote_t = f'{REMOTE_DIR}/templates/{t}'
            if os.path.exists(local_t):
                print(f"Uploading {t} to {remote_t}...")
                sftp.put(local_t, remote_t)
        
        # 3. Upload translations
        local_tr = os.path.join(os.getcwd(), 'backend', 'config', 'translations_tr.json')
        remote_tr = f'{REMOTE_DIR}/backend/config/translations_tr.json'
        if os.path.exists(local_tr):
             print(f"Uploading translations to {remote_tr}...")
             sftp.put(local_tr, remote_tr)
        
        sftp.close()
        print("Uploads complete.")
        
        # 4. Restart Service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code == 0:
            print("Service restarted successfully via systemctl.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")
            # Try kill and manual start as fallback
            client.exec_command("pkill -f 'python web_app.py'")
            time.sleep(2)
            # Assuming venv exists based on deploy_update.py
            cmd = f"nohup {REMOTE_DIR}/venv/bin/python {REMOTE_DIR}/web_app.py > {REMOTE_DIR}/app.log 2>&1 &"
            client.exec_command(cmd)
            print("Attempted manual restart.")

        # Check status
        time.sleep(2)
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_fix()
