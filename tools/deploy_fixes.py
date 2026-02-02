import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

FILES = [
    "templates/base.html",
    "templates/dashboard.html",
    "templates/social.html",
    "templates/prioritization.html",
    "templates/tcfd.html",
    "templates/surveys.html",
    "templates/ungc.html",
    "templates/sdg.html",
    "templates/issb.html",
    "templates/gri.html",
    "templates/esg.html",
    "templates/targets.html",
    "templates/reporting_journey.html",
    "templates/mapping.html",
    "web_app.py"
]

LOCAL_BASE = r"c:\SUSTAINAGESERVER"
REMOTE_BASE = "/var/www/sustainage"

def deploy():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        for rel_path in FILES:
            local_path = os.path.join(LOCAL_BASE, rel_path)
            remote_path = f"{REMOTE_BASE}/{rel_path.replace(os.sep, '/')}"
            
            if os.path.exists(local_path):
                print(f"Uploading {rel_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"Warning: Local file not found: {local_path}")
                
        sftp.close()
        
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output: {err}")
        
        ssh.close()
        print("Deploy completed successfully.")
        
    except Exception as e:
        print(f"Deploy failed: {str(e)}")

if __name__ == "__main__":
    deploy()
