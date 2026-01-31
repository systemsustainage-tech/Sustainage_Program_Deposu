import paramiko
import os
import time

# Server credentials
HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_DIR = "/var/www/sustainage"

def deploy_and_debug():
    try:
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        sftp = ssh.open_sftp()
        
        print("Connected to server.")

        # 1. Upload create_survey_tables
        files_to_deploy = [
            ("tools/create_survey_tables.py", "tools/create_survey_tables.py")
        ]

        for local, remote in files_to_deploy:
            local_path = os.path.join(os.getcwd(), local)
            remote_path = f"{REMOTE_DIR}/{remote}"
            print(f"Uploading {local} to {remote_path}...")
            sftp.put(local_path, remote_path)

        # 2. Run Create Tables
        print("Running Create Survey Tables...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_DIR}/tools/create_survey_tables.py")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        sftp.close()
        ssh.close()
        print("\nVerification complete.")
        
        sftp.close()
        ssh.close()
        print("\nDiagnostic check complete.")

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy_and_debug()
