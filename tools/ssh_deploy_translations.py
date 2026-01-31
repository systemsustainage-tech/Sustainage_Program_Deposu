import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES_TO_DEPLOY = [
    (os.path.join(BASE_DIR, "locales", "tr.json"), "/var/www/sustainage/locales/tr.json"),
    (os.path.join(BASE_DIR, "locales", "en.json"), "/var/www/sustainage/locales/en.json"),
    (os.path.join(BASE_DIR, "backend", "config", "translations_tr.json"), "/var/www/sustainage/backend/config/translations_tr.json"),
    (os.path.join(BASE_DIR, "remote_web_app.py"), "/var/www/sustainage/web_app.py"),
    (os.path.join(BASE_DIR, "templates", "governance_edit.html"), "/var/www/sustainage/templates/governance_edit.html"),
    (os.path.join(BASE_DIR, "templates", "economic.html"), "/var/www/sustainage/templates/economic.html"),
    (os.path.join(BASE_DIR, "templates", "economic_edit.html"), "/var/www/sustainage/templates/economic_edit.html"),
    (os.path.join(BASE_DIR, "templates", "esg.html"), "/var/www/sustainage/templates/esg.html"),
    (os.path.join(BASE_DIR, "templates", "esg_edit.html"), "/var/www/sustainage/templates/esg_edit.html"),
    (os.path.join(BASE_DIR, "backend", "modules", "esg", "esg_manager.py"), "/var/www/sustainage/backend/modules/esg/esg_manager.py"),
    (os.path.join(BASE_DIR, "backend", "config", "esg_config.json"), "/var/www/sustainage/backend/config/esg_config.json"),
]

def deploy():
    print("--- Deploying Translations & Templates ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        for local, remote in FILES_TO_DEPLOY:
            if os.path.exists(local):
                print(f"Uploading {os.path.basename(local)}...")
                sftp.put(local, remote)
            else:
                print(f"Skipping missing file: {local}")
        
        sftp.close()
        
        print("Restarting Gunicorn to refresh locales...")
        ssh.exec_command("pkill -HUP gunicorn")
        
        ssh.close()
        print("--- Deployment Complete ---")
        
    except Exception as e:
        print(f"Deployment Failed: {e}")

if __name__ == "__main__":
    deploy()
