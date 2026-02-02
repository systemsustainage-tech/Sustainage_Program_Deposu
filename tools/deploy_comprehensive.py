import paramiko
import os
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

FILES_TO_DEPLOY = [
    # Core
    { "local": "c:/SUSTAINAGESERVER/web_app.py", "remote": "/var/www/sustainage/web_app.py" },
    { "local": "c:/SUSTAINAGESERVER/remote_web_app.py", "remote": "/var/www/sustainage/remote_web_app.py" },
    { "local": "c:/SUSTAINAGESERVER/locales/tr.json", "remote": "/var/www/sustainage/locales/tr.json" },
    { "local": "c:/SUSTAINAGESERVER/backend/locales/tr.json", "remote": "/var/www/sustainage/backend/locales/tr.json" },
    
    # Templates - Main Modules
    { "local": "c:/SUSTAINAGESERVER/templates/dashboard.html", "remote": "/var/www/sustainage/templates/dashboard.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/social.html", "remote": "/var/www/sustainage/templates/social.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/governance.html", "remote": "/var/www/sustainage/templates/governance.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/economic.html", "remote": "/var/www/sustainage/templates/economic.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/stakeholder.html", "remote": "/var/www/sustainage/templates/stakeholder.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/environmental.html", "remote": "/var/www/sustainage/templates/environmental.html" },
    
    # Templates - Social Sub-modules
    { "local": "c:/SUSTAINAGESERVER/templates/labor.html", "remote": "/var/www/sustainage/templates/labor.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/human_rights.html", "remote": "/var/www/sustainage/templates/human_rights.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/supply_chain.html", "remote": "/var/www/sustainage/templates/supply_chain.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/community.html", "remote": "/var/www/sustainage/templates/community.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/consumer.html", "remote": "/var/www/sustainage/templates/consumer.html" },
    
    # Templates - Surveys
    { "local": "c:/SUSTAINAGESERVER/templates/surveys.html", "remote": "/var/www/sustainage/templates/surveys.html" },
    { "local": "c:/SUSTAINAGESERVER/templates/survey_response_detail.html", "remote": "/var/www/sustainage/templates/survey_response_detail.html" },
]

def deploy():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        
        print("Uploading files...")
        for file in FILES_TO_DEPLOY:
            try:
                if os.path.exists(file["local"]):
                    print(f"Uploading {os.path.basename(file['local'])}...")
                    sftp.put(file["local"], file["remote"])
                else:
                    print(f"Warning: Local file not found: {file['local']}")
            except Exception as e:
                print(f"Error uploading {file['local']}: {e}")
                
        sftp.close()
        
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")
            
        ssh.close()
        print("Deployment completed.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    deploy()
