import paramiko
import os

# Server Config
HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

# Files to Sync
FILES = [
    {"local": r"c:\SDG\locales\tr.json", "remote": "/var/www/sustainage/locales/tr.json"},
    {"local": r"c:\SDG\locales\en.json", "remote": "/var/www/sustainage/locales/en.json"},
    {"local": r"c:\SDG\server\templates\energy.html", "remote": "/var/www/sustainage/server/templates/energy.html"},
    {"local": r"c:\SDG\server\templates\waste.html", "remote": "/var/www/sustainage/server/templates/waste.html"},
    {"local": r"c:\SDG\server\templates\water.html", "remote": "/var/www/sustainage/server/templates/water.html"},
    {"local": r"c:\SDG\server\templates\company_edit.html", "remote": "/var/www/sustainage/server/templates/company_edit.html"},
    {"local": r"c:\SDG\server\templates\user_edit.html", "remote": "/var/www/sustainage/server/templates/user_edit.html"},
    {"local": r"c:\SDG\server\templates\report_edit.html", "remote": "/var/www/sustainage/server/templates/report_edit.html"},
    {"local": r"c:\SDG\server\templates\help.html", "remote": "/var/www/sustainage/server/templates/help.html"}
]

def deploy():
    print("--- Deploying Remaining Template Refactors ---")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        for item in FILES:
            try:
                sftp.put(item["local"], item["remote"])
                print(f"Uploaded: {item['local']} -> {item['remote']}")
            except Exception as e:
                print(f"Error uploading {item['local']}: {e}")
                
        # Restart Gunicorn
        print("Restarting Gunicorn...")
        ssh.exec_command("pkill -HUP gunicorn")
        
        sftp.close()
        ssh.close()
        print("--- Deployment Complete ---")
        
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    deploy()
