
import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"

FILES_TO_DEPLOY = [
    {
        "local": "c:\\SDG\\server\\web_app.py",
        "remote": "/var/www/sustainage/web_app.py"
    },
    {
        "local": "c:\\SDG\\carbon\\carbon_calculator.py",
        "remote": "/var/www/sustainage/backend/carbon/carbon_calculator.py"
    },
    {
        "local": "c:\\SDG\\carbon\\carbon_manager.py",
        "remote": "/var/www/sustainage/backend/carbon/carbon_manager.py"
    },
    {
        "local": "c:\\SDG\\yonetim\\kullanici_yonetimi\\models\\user_manager.py",
        "remote": "/var/www/sustainage/backend/yonetim/kullanici_yonetimi/models/user_manager.py"
    },
    {
        "local": "c:\\SDG\\templates\\dashboard.html",
        "remote": "/var/www/sustainage/templates/dashboard.html"
    },
    {
        "local": "c:\\SDG\\templates\\base.html",
        "remote": "/var/www/sustainage/templates/base.html"
    }
]

def deploy():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        sftp = ssh.open_sftp()
        
        for item in FILES_TO_DEPLOY:
            local = item["local"]
            remote = item["remote"]
            
            if not os.path.exists(local):
                print(f"Warning: Local file not found: {local}")
                continue
                
            print(f"Uploading {local} to {remote}...")
            try:
                # Ensure remote directory exists
                remote_dir = os.path.dirname(remote)
                try:
                    sftp.stat(remote_dir)
                except FileNotFoundError:
                    # Recursive directory creation not supported directly, assumed mostly existing
                    pass
                
                sftp.put(local, remote)
            except Exception as e:
                print(f"Error uploading {local}: {e}")
        
        sftp.close()
        
        print("Restarting sustainage service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        ssh.close()
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
