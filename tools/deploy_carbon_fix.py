import paramiko
import sys
import os

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

FILE_TO_UPLOAD = 'c:/SUSTAINAGESERVER/backend/modules/environmental/emission_factor_data.py'
REMOTE_PATH = '/var/www/sustainage/backend/modules/environmental/emission_factor_data.py'

def upload_file():
    print(f"Uploading {FILE_TO_UPLOAD} to {REMOTE_PATH}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
        sftp = ssh.open_sftp()
        try:
            sftp.put(FILE_TO_UPLOAD, REMOTE_PATH)
            print(f"Uploaded {REMOTE_PATH}")
        except Exception as e:
            print(f"Failed to upload: {e}")
        sftp.close()
        
        # Restart service
        print("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")
            
        ssh.close()
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    upload_file()
