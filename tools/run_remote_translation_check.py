import paramiko
import sys
import os

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_SCRIPT = 'c:/SUSTAINAGESERVER/tools/check_translation_remote.py'
REMOTE_SCRIPT = '/var/www/sustainage/tools/check_translation_remote.py'

def run_check():
    print(f"Uploading {LOCAL_SCRIPT}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
        sftp = ssh.open_sftp()
        try:
            sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
            print(f"Uploaded {REMOTE_SCRIPT}")
        except Exception as e:
            print(f"Failed to upload: {e}")
        sftp.close()
        
        print("Running check...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_SCRIPT}")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error: {err}")
            
        ssh.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    run_check()
