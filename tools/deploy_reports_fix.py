import paramiko
import os

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

LOCAL_FILE = r"c:\SUSTAINAGESERVER\templates\reports.html"
REMOTE_FILE = "/var/www/sustainage/templates/reports.html"

def deploy():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()
        
        print(f"Uploading {LOCAL_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        
        sftp.close()
        
        # Restart not strictly necessary for template change but good practice if caching
        # print("Restarting service...")
        # ssh.exec_command("systemctl restart sustainage")
        
        ssh.close()
        print("Deploy completed successfully.")
        
    except Exception as e:
        print(f"Deploy failed: {str(e)}")

if __name__ == "__main__":
    deploy()
