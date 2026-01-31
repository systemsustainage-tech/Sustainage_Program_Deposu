
import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

LOCAL_SCRIPT = 'c:\\SUSTAINAGESERVER\\tools\\remote_tcfd_check.py'
REMOTE_SCRIPT = '/tmp/remote_tcfd_check.py'

def run_check():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        print(f"Uploading {LOCAL_SCRIPT} to {REMOTE_SCRIPT}...")
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()
        
        print("Running remote check script...")
        stdin, stdout, stderr = client.exec_command(f"python3 {REMOTE_SCRIPT}")
        
        print("Output:")
        print(stdout.read().decode())
        print("Errors:")
        print(stderr.read().decode())
        
        # Cleanup
        client.exec_command(f"rm {REMOTE_SCRIPT}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_check()
