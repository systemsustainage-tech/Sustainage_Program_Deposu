import paramiko
import os
import time

def deploy_cbam_cdp():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_base = '/var/www/sustainage'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    files_to_deploy = [
        ('backend/modules/cbam/cbam_manager.py', 'backend/modules/cbam/cbam_manager.py'),
        ('backend/modules/cdp/cdp_manager.py', 'backend/modules/cdp/cdp_manager.py'),
        ('backend/modules/cdp/cdp_questions.json', 'backend/modules/cdp/cdp_questions.json'),
        ('templates/cbam_edit.html', 'templates/cbam_edit.html'),
        ('templates/cdp_settings.html', 'templates/cdp_settings.html'),
        ('remote_web_app.py', 'web_app.py'),
    ]

    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        for local, remote in files_to_deploy:
            local_path = os.path.abspath(local)
            remote_path = f"{remote_base}/{remote}"
            print(f"Uploading {local} -> {remote_path}...")
            sftp.put(local_path, remote_path)
            
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")

    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_cbam_cdp()
