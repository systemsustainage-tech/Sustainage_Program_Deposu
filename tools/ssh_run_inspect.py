
import paramiko
import os
import time

# Server Credentials
HOST = "72.62.150.207"
USER = "root"
PASS = "Z/2m?-JDp5VaX6q+HO(b"

LOCAL_SCRIPT = r"c:\SDG\tools\remote_inspect_tables.py"
REMOTE_SCRIPT = "/var/www/sustainage/tools/remote_inspect_tables.py"

def run_inspection():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        try:
            sftp.mkdir("/var/www/sustainage/tools")
        except IOError:
            pass
            
        print(f"Uploading {LOCAL_SCRIPT} to {REMOTE_SCRIPT}...")
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()
        
        print("Running inspection script...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_SCRIPT}")
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print("\n[OUTPUT]")
        print(output)
        
        if error:
            print("\n[ERROR]")
            print(error)
            
        ssh.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_inspection()
