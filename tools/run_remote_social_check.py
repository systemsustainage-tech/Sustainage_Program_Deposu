import paramiko
import os

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = os.environ.get("REMOTE_SSH_PASS", "Kayra_1507")

def run_remote_check():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Upload the check script
        sftp = client.open_sftp()
        local_script = 'tools/remote_social_check.py'
        remote_script = '/root/remote_social_check.py'
        sftp.put(local_script, remote_script)
        sftp.close()
        
        # Run the script
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_script}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_remote_check()
