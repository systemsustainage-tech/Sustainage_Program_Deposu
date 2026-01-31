import paramiko
import os
import sys

# Server Details
HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"
LOCAL_SCRIPT = "c:\\SDG\\tools\\remote_schema_fix_columns.py"
REMOTE_SCRIPT = "/var/www/sustainage/tools/remote_schema_fix_columns.py"

def deploy_and_run():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        # Create tools dir if not exists
        ssh.exec_command("mkdir -p /var/www/sustainage/tools")
        
        sftp = ssh.open_sftp()
        print(f"Uploading {LOCAL_SCRIPT} to {REMOTE_SCRIPT}...")
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()
        
        print("Running script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_SCRIPT}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
        return True
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    deploy_and_run()
