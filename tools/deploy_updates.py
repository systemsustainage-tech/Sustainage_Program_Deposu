
import paramiko
import os
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

FILES_TO_DEPLOY = [
    {
        "local": "c:/SUSTAINAGESERVER/web_app.py",
        "remote": "/var/www/sustainage/web_app.py"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/human_rights.html",
        "remote": "/var/www/sustainage/templates/human_rights.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/supply_chain.html",
        "remote": "/var/www/sustainage/templates/supply_chain.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/supply_chain_profile.html",
        "remote": "/var/www/sustainage/templates/supply_chain_profile.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/users.html",
        "remote": "/var/www/sustainage/templates/users.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/includes/pagination.html",
        "remote": "/var/www/sustainage/templates/includes/pagination.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/labor.html",
        "remote": "/var/www/sustainage/templates/labor.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/consumer.html",
        "remote": "/var/www/sustainage/templates/consumer.html"
    },
    {
        "local": "c:/SUSTAINAGESERVER/templates/community.html",
        "remote": "/var/www/sustainage/templates/community.html"
    }
]

def deploy():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        
        for item in FILES_TO_DEPLOY:
            local_path = item['local']
            remote_path = item['remote']
            
            if os.path.exists(local_path):
                print(f"Uploading {local_path} -> {remote_path}")
                try:
                    sftp.put(local_path, remote_path)
                except Exception as e:
                    print(f"Error uploading {local_path}: {e}")
            else:
                print(f"Local file not found: {local_path}")
                
        sftp.close()
        
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
        print("Deployment completed successfully.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
