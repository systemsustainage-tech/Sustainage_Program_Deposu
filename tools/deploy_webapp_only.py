import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
REMOTE_PATH = "/var/www/sustainage/web_app.py"
LOCAL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web_app.py"))
REMOTE_DASHBOARD = "/var/www/sustainage/templates/dashboard.html"
LOCAL_DASHBOARD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "dashboard.html"))

def deploy():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {HOST} as {USER}...")
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        # Upload web_app.py
        sftp = ssh.open_sftp()
        print(f"Uploading {LOCAL_PATH} to {REMOTE_PATH}...")
        sftp.put(LOCAL_PATH, REMOTE_PATH)
        
        # Upload dashboard.html template explicitly
        print(f"Uploading {LOCAL_DASHBOARD} to {REMOTE_DASHBOARD}...")
        sftp.put(LOCAL_DASHBOARD, REMOTE_DASHBOARD)
        sftp.close()
        
        # Restart Service
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out: print("STDOUT:", out)
        if err: print("STDERR:", err)
        
        ssh.close()
        print("Deployment and restart complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy()
