import paramiko
import os
import sys

# Server details
HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"
REMOTE_PATH = "/var/www/sustainage"

def deploy_dashboard():
    try:
        transport = paramiko.Transport((HOST, 22))
        transport.connect(username=USER, password=PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        local_file = r"c:\SDG\templates\dashboard.html"
        remote_file = f"{REMOTE_PATH}/templates/dashboard.html"
        
        print(f"Uploading {local_file} to {remote_file}...")
        sftp.put(local_file, remote_file)
        print("Upload successful.")
        
        sftp.close()
        transport.close()
        return True
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    if deploy_dashboard():
        print("Dashboard deployed successfully.")
    else:
        sys.exit(1)
